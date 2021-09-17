# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added

### Fixed

### Changed

### Deprecated

### Removed

## [v8]
### Added
- Add ticket description to generated comment from `post-jira-comment` action.

### Fixed
- Fix input ref in `publish-release` action so Github release points to correct commit.

## [v7]
### Changed
- (GS-16529) Change `analyze-test-results` to look for `Failed` tests to reduce false positives.

## [v6]
### Added
- (GS-16529) Added an action for analyzing Unity test runner results.

## [v5]
### Fixed
- Fix `publish-release` to properly use input `ref` for release target branch.

## [v4]
### Fixed
- Update various Octokit API calls to match the structure of the newer version being used.

## [v3]
### Fixed
- Regenerate distribution JavaScript for `check-for-changelog` action.
- Fix `check-for-documentation` action to properly take JIRA credentials as inputs.

## [v2]
### Added
- (GS-16377) Port `check-for-changelog`, `check-for-documentation` and `post-jira-comment` quality check actions from UnityCore.

## [v1]
### Added
- (GS-16377) Import `post-to-slack`, `publish-release`, `update-changelog` and `update-package-json` actions from UnityCore.

[Unreleased]: https://github.com/mindjolt/uc-actions/tree/HEAD
[v8]: https://github.com/mindjolt/uc-actions/tree/v8
[v7]: https://github.com/mindjolt/uc-actions/tree/v7
[v6]: https://github.com/mindjolt/uc-actions/tree/v6
[v5]: https://github.com/mindjolt/uc-actions/tree/v5
[v4]: https://github.com/mindjolt/uc-actions/tree/v4
[v3]: https://github.com/mindjolt/uc-actions/tree/v3
[v2]: https://github.com/mindjolt/uc-actions/tree/v2
[v1]: https://github.com/mindjolt/uc-actions/tree/v1
