# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- (GS-19257) Added workflows and actions for automated performance analysis.

### Fixed

### Changed
- (GS-19049) Modified flows to announce published packages in `sdk_announce` by default
- (GS-18736) Modified test-builds and unit-tests workflows to use new UnityCoreTests structure.
- (GS-19076) Replaced deprecated set-output commands in workflows and actions.
- (GS-19007) Updated `test-builds` and `unit-tests` workflows to use Unity versions 2020.3.44f1 and 2021.3.18f1.
- (GS-19256) Changed `unit-tests` workflow to exclude `Performance` tests.
- (GS-19376) Adjusted Slack message used by `publish-package` workflow.
- (GS-19528) Updated `checkout` to `v3` in advance of `v2`'s deprecation.

### Deprecated

### Removed
- (GS-19049) Removed deprecated `package-release` and `-snapshot` workflows

## [v12]
### Added
- (GS-18938) Added an action for modifying scripting define symbols in Unity projects.

## [v11]
### Added
- (GS-18575) Added a generic package publishing workflow.

### Changed
- (GS-18679) Upgrade dependencies and move actions to `node16` environment.

## [v10]
### Changed
- (GS-18039) Renamed documentation `index.md` to `README.md` so GitHub can find it.
- (GS-18110) Removed hard-coded `UnityCore` references from workflow variables.

## [v9]
### Added
- Added build-with-ubp action.

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
[v12]: https://github.com/mindjolt/uc-actions/tree/v12
[v11]: https://github.com/mindjolt/uc-actions/tree/v11
[v10]: https://github.com/mindjolt/uc-actions/tree/v10
[v9]: https://github.com/mindjolt/uc-actions/tree/v9
[v8]: https://github.com/mindjolt/uc-actions/tree/v8
[v7]: https://github.com/mindjolt/uc-actions/tree/v7
[v6]: https://github.com/mindjolt/uc-actions/tree/v6
[v5]: https://github.com/mindjolt/uc-actions/tree/v5
[v4]: https://github.com/mindjolt/uc-actions/tree/v4
[v3]: https://github.com/mindjolt/uc-actions/tree/v3
[v2]: https://github.com/mindjolt/uc-actions/tree/v2
[v1]: https://github.com/mindjolt/uc-actions/tree/v1
