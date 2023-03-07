const core = require('@actions/core');
const github = require('@actions/github');


const getExistingComment = async (parameters) => {
  if (parameters.mode !== 'create') {
    const comments = await core.group('Fetching existing comments', async () => {
      return await parameters.api.paginate(
          parameters.api.rest.issues.listComments.endpoint.merge({
            owner: parameters.context.issue.owner,
            repo: parameters.context.issue.repo,
            issue_number: parameters.context.issue.number,
          }));
    });

    const firstLine = `**${parameters.title}**\n`;

    for (const comment of comments) {
      if (comment.body.startsWith(firstLine)) {
        core.info('Found existing comment');
        return comment;
      }
    }
  }

  return null;
};


const createComment = async (parameters, _) => {
  return parameters.api.rest.issues.createComment({
      owner: parameters.context.repo.owner,
      repo: parameters.context.repo.repo,
      issue_number: parameters.context.issue.number,
      body: `**${parameters.title}**\n${parameters.body}`,
  });
};


const replaceComment = async (parameters, existingComment) => {
  return parameters.api.rest.issues.updateComment({
      owner: parameters.context.repo.owner,
      repo: parameters.context.repo.repo,
      comment_id: existingComment.id,
      body: `**${parameters.title}**\n${parameters.body}`,
  });
};


const amendComment = async (parameters, existingComment) => {
  const newCommentBody = existingComment.body.split('\n').slice(1).map((line) => {
    const prelude = line.match(/^\s*[\*-] /) || [''];
    const parts = [prelude[0], line.substr(prelude[0].length)];

    return `${parts[0]}~~${parts[1].replace('~~', '')}~~`;
  }).join('\n') + `\n${parameters.body}`;

  return replaceComment({...parameters, 'body': newCommentBody}, existingComment);
};


const createNewCommentOr = (func) => {
  return async (parameters, existingComment) => {
    if (existingComment === null) {
      await createComment(parameters, existingComment);
    } else {
      func(parameters, existingComment);
    }
  };
};


(async () => {
  try {
    const parameters = {
      'context': github.context,
      'api': github.getOctokit(core.getInput('github_token', { required: true })),
      'mode': core.getInput('mode', { required: true }),
      'title': core.getInput('title', { required: true }),
      'body': core.getInput('body', { required: true }),
    };

    await {
      'amend': createNewCommentOr(amendComment),
      'create': createComment,
      'new': createNewCommentOr(() => {}),
      'replace': createNewCommentOr(replaceComment),
    }[parameters.mode](parameters, await getExistingComment(parameters));
  } catch (error) {
    core.setFailed(error.message);
  }
})();
