# Create package action

This action is responsible for creating a distributable package from the
configuration found within a repository.  When properly invoked, this will
generate both a `package.zip` and `package.json` file that can be uploaded to
the package github repository.

## Inputs

This action requires three inputs to function correctly:

* `package_version` - version of the package being created
* `source_path` - full path to the package contents to be built
    * _Note: This path should contain the `package.properties` file._

## Outputs

Upon successful completion, this action outputs two string values:

* `json_path` - full path to the `package.json` file that was generated
* `zip_path` - full path to the `package.zip` file that was generated

## Building locally

This action may also be used to locally build a package, for example to install
a local, working copy of a project via the package manager.  The follow steps
will describe the process of building a package manually.

### Navigate to the action directory

All of these steps should be performed from the `create-package-github` directory found
in this repository.

```bash
cd /path/to/repositories/uc-actions/create-package-github
```

### Ensure the resources directory exists

When the packaging code is built, it will look for a `package.properties` file
located in the main `resources` directory.  Create this directory if it does not
already exist:

```bash
mkdir -p src/main/resources
```

### Copy the project's package.properties file

Next, the `package.properties` file of the project being built needs to be
placed in the `resources` directory:

```bash
cp /path/to/repositories/my-project/package.properties src/main/resources/
```

### Finish the package configuration

The `package.properties` file used by the builder requires two additional fields
to be added in order to run successfully.  This can be accomplished by simply
editing `src/main/resources/package.properties` and adding them to the file.

* `sourcePath` - full path to the project; same as `source_path` input above
* `packageVersion` - package version to build; same as `package_version` input above

Example `package.properties`:

    packageName=MyProjectSdk
    ...
    sourcePath=/path/to/repositories/my-project/
    packageVersion=1.0.0

### Execute the Gradle task

Once all of the configuration has been completed, the Gradle task can be invoked
to attempt to build the project:

```bash
./gradlew createPackage
```

If successful, the generated artifacts will be placed within a `build` directory.
