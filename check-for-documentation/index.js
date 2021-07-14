const core = require('@actions/core');
const github = require('@actions/github');
const fetch = require('node-fetch');


async function run()
{
    try
    {
        const context = github.context;
        const token = core.getInput('github_token', { required: true });
        const api = github.getOctokit(token);

        const jiraNumber = context.payload.pull_request.title.match(/^GS-[0-9]+/g);

        if (jiraNumber)
        {
            const jiraTicketNumber = jiraNumber[0];

            var request = {
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Basic ${Buffer.from(`${core.getInput('jira_user')}:${core.getInput('jira_password')}`).toString('base64')}`,
                }
            };

            var jiraResponse = await fetch(`https://socialgamingnetwork.jira.com/rest/api/latest/issue/${jiraTicketNumber}?fields=labels`, request);
            var jiraJSON = await jiraResponse.json();

            core.debug(jiraJSON);

            if (jiraResponse.ok)
            {
                if (jiraJSON.fields.labels.includes('Documentation'))
                {
                    var documentationChangeFound = false;

                    const files = await api.paginate(api.pulls.listFiles.endpoint.merge({
                        owner: context.issue.owner,
                        repo: context.issue.repo,
                        pull_number: context.issue.number,
                        per_page: 3000,
                    }));

                    for (const file of files)
                    {
                        if (file.filename.search(`Editor/Documentation/.+`) !== -1)
                        {
                            core.info('Found documentation changes');
                            documentationChangeFound = true;
                            break;
                        }
                    }

                    if (!documentationChangeFound)
                    {
                      core.setFailed('Markdown documentation update is required but was not updated');
                    }
                }
                else
                {
                    core.info(`JIRA issue ${jiraTicketNumber} does not have a Documentation label, so all is well`)
                }
            }
            else
            {
                core.setFailed('There was an issue with the JIRA API');
            }
        }
        else
        {
            core.info('No JIRA ticket was found in the pull request title');
        }
    }
    catch (error)
    {
        core.setFailed(error.message);
    }
}

run();
