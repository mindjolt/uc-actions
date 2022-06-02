const core = require('@actions/core');
const github = require('@actions/github');


async function run()
{
    try
    {
        const context = github.context;
        const token = core.getInput('github_token', { required: true });
        const filename = core.getInput('filename', { required: true });
        const api = github.getOctokit(token);

        var changelogFound = false;

        const files = await api.paginate(api.rest.pulls.listFiles.endpoint.merge({
            owner: context.issue.owner,
            repo: context.issue.repo,
            pull_number: context.issue.number,
            per_page: 3000,
        }));

        for (const file of files)
        {
            if (file.filename == filename)
            {
                core.info(`Found the ${filename} update`);
                changelogFound = true;
                break;
            }
        }

        if (!changelogFound)
        {
            core.setFailed(`${filename} was not updated`);
        }
    }
    catch (error)
    {
        core.setFailed(error.message);
    }
}

run();
