const core = require('@actions/core');
const github = require('@actions/github');
const fetch = require('node-fetch');


async function run()
{
    try
    {
        const context = github.context;
        const jiraProjectPrefix = core.getInput('jira_project_prefix', { required: true }).toUpperCase();
        const jiraStatusId = core.getInput('jira_status_id', { required: true });
        const jiraStatusTransitionId = core.getInput('jira_status_transition_id', { required: true });

        const jiraNumber = context.payload.pull_request.title.match(new RegExp(`${jiraProjectPrefix}-[0-9]+`, "g"));

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

            var jiraResponse = await fetch(`https://socialgamingnetwork.jira.com/rest/api/latest/issue/${jiraTicketNumber}?fields=status`, request);
            var jiraJSON = await jiraResponse.json();

            core.debug(jiraJSON);

            if (jiraResponse.ok)
            {
                if (jiraJSON.fields.status.id == jiraStatusId)
                {
                    var postRequest = {
                        method: 'POST',
                        credentials: 'include',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Basic ${Buffer.from(`${core.getInput('jira_user')}:${core.getInput('jira_password')}`).toString('base64')}`,
                        },
                        body: JSON.stringify({
                            transition: {
                                id: `${jiraStatusTransitionId}`
                            }
                        })
                    };

                    core.debug(postRequest);

                    var jiraPOSTResponse = await fetch(`https://socialgamingnetwork.jira.com/rest/api/latest/issue/${jiraTicketNumber}/transitions`, postRequest);

                    if (jiraPOSTResponse.ok)
                    {
                        core.info('JIRA ticket status transition successful');
                    }
                    else
                    {
                        core.setFailed('There was an issue using the JIRA API to transition the ticket status');
                    }
                }
                else
                {
                    core.info('JIRA ticket status does not match');
                }
            }
            else
            {
                core.setFailed('There was an issue fetching ticket status with the JIRA API');
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
