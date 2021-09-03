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
            const issues = await core.group('Fetching existing comments', async () => {
                return await api.paginate(api.rest.issues.listComments.endpoint.merge({
                    owner: context.issue.owner,
                    repo: context.issue.repo,
                    issue_number: context.issue.number,
                }));
            });

            var previousCommentFound = false;

            for (const issue of issues)
            {
                if (issue.body.includes('Link to JIRA Ticket'))
                {
                    core.info('Found JIRA comment');
                    previousCommentFound = true;
                    break;
                }
            }

            if (!previousCommentFound)
            {
                const jiraTicketNumber = jiraNumber[0];

                var request = {
                    credentials: 'include',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Basic ${Buffer.from(`${core.getInput('jira_user')}:${core.getInput('jira_password')}`).toString('base64')}`,
                    }
                };

                var jiraResponse = await fetch(`https://socialgamingnetwork.jira.com/rest/api/latest/issue/${jiraTicketNumber}?fields=description`, request);
                var jiraJSON = await jiraResponse.json();

                core.debug(jiraJSON);

                if (jiraResponse.ok)
                {
                    var bodyString = `Link to JIRA Ticket: [${jiraTicketNumber}]\n\n`
                    bodyString += 'Please double check that your commits follow the [Git Commit Guidelines](https://socialgamingnetwork.jira.com/wiki/spaces/SFIOW/pages/1633026412/Git+Commit+Guidelines) :)\n\n'
                    bodyString += `[${jiraTicketNumber}]: https://socialgamingnetwork.jira.com/browse/${jiraTicketNumber}`
                    bodyString += '---\n'
                    bodyString += jiraJSON.fields.description

                    core.info(`No comment found. Adding new comment: '${bodyString}'`)

                    api.rest.issues.createComment({
                        owner: context.repo.owner,
                        repo: context.repo.repo,
                        issue_number: context.issue.number,
                        body: bodyString,
                    });
                }
                else
                {
                    core.setFailed('There was an issue with the JIRA API');
                }
            }
        }
        else
        {
          core.info('No JIRA ticket was found in the pull request title :(');
        }
    }
    catch (error)
    {
        core.setFailed(error.message);
    }
}

run();
