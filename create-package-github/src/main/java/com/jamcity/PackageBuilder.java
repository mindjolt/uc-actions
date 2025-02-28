package com.jamcity;

import com.jamcity.jcpm.JamCityPackage;
import com.jamcity.jcpm.PackagerConfig;

import java.io.File;
import java.io.IOException;
import java.net.URI;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.text.SimpleDateFormat;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class PackageBuilder {
    public static void main(String[] args) throws Exception {
        final Map<String, String> packageProperties = getPackageProperties(ResourceBundle.getBundle("package"));

        final String packageName = packageProperties.get("packageName");
        final String packageVersion = packageProperties.get("packageVersion");
        final String sourcePath = packageProperties.get("sourcePath");
        final String outputPath = packageProperties.getOrDefault("outputPath", "build");
        final List<String> excludePaths = getListFromString(packageProperties.getOrDefault("excludePaths", ""));
        final List<String> dependencies = getListFromString(packageProperties.getOrDefault("dependencies", ""));
        final List<String> optionalDependencies = getListFromString(packageProperties.getOrDefault("optionalDependencies", ""));

        if (!Files.exists(Paths.get(sourcePath))) {
            throw new IllegalArgumentException(String.format("Source path '%s' does not exist.", sourcePath));
        }

        createDirectoryRecursively(Paths.get(outputPath));

        var packageBuilder = JamCityPackage.builder()
                .name(packageName)
                .displayName(packageProperties.getOrDefault("displayName", packageName))
                .description(packageProperties.getOrDefault("description", packageName))
                .version(packageVersion);

        if (packageProperties.containsKey("homepageUri")) {
            packageBuilder.homepage(new URI(packageProperties.get("homepageUri")));
        }

        if (packageProperties.containsKey("changelogUri")) {
            String changelogUri = packageProperties.get("changelogUri");

            if (!changelogUri.contains("#")) {
                final String anchorName = String.format("%s---%s",
                        packageVersion.replaceAll("\\.", ""),
                        new SimpleDateFormat("yyyy-MM-dd").format(new Date()));

                changelogUri = String.format("%s#%s", changelogUri, anchorName);
                packageProperties.put("changelogUri", changelogUri);
            }

            packageBuilder.changelog(new URI(changelogUri));
        }

        addPackageDependencies(packageBuilder, dependencies, JamCityPackage.DependencyScope.Required);
        addPackageDependencies(packageBuilder, optionalDependencies, JamCityPackage.DependencyScope.Optional);

        var jamCityPackage = packageBuilder.buildTargetDir(outputPath).build();
        var logger = jamCityPackage.getLevelLogger();

        logger.accept(JamCityPackage.LogLevel.Info, "Creating package with the following properties:");

        for (String key : packageProperties.keySet()) {
            logger.accept(JamCityPackage.LogLevel.Info, String.format("%s = %s", key, packageProperties.get(key)));
        }

        PackagerConfig.builder()
                .jcPackage(jamCityPackage)
                .generateAsmdef("true".equals(packageProperties.getOrDefault("generateAsmdef", "true")))

                .directory(new File(sourcePath), (dir, name) -> {
                    final Path absolutePath = Paths.get(dir.toString(), name);
                    final String relativePath = Paths.get(sourcePath).relativize(absolutePath).toString();

                    return !name.startsWith(".") &&
                            !"package.json".equals(name) &&
                            !"package.json.meta".equals(name) &&
                            !"package.properties".equals(name) &&
                            !"package.properties.meta".equals(name) &&
                            !"JamCityBuildInfo.cs".equals(name) &&
                            !excludePaths.contains(relativePath);
                })

                .build()
                .writePackage();
    }

    private static Map<String, String> getPackageProperties(ResourceBundle resourceBundle) {
        final Pattern substitution = Pattern.compile("\\$\\{(\\w+)}");

        final var keys = resourceBundle.getKeys();
        final var inputs = new HashMap<String, String>();
        final var outputs = new HashMap<String, String>();

        while (keys.hasMoreElements()) {
            final String key = keys.nextElement();
            inputs.put(key, resourceBundle.getString(key));
        }

        while (!inputs.isEmpty()) {
            final int count = inputs.size();

            for (var key : inputs.keySet()) {
                String value = inputs.get(key);
                Matcher matcher = substitution.matcher(value);
                boolean found = matcher.find();

                while (found) {
                    final String name = matcher.group(1);

                    if (outputs.containsKey(name)) {
                        value = value.replace(String.format("${%s}", name), outputs.get(name));
                        matcher = substitution.matcher(value);
                        found = matcher.find();
                    } else {
                        break;
                    }
                }

                if (!found) {
                    inputs.remove(key);
                    outputs.put(key, value);
                    break;
                }
            }

            if (count == inputs.size()) {
                throw new IllegalArgumentException("Unresolved circular dependency in package properties");
            }
        }

        return outputs;
    }

    private static void createDirectoryRecursively(Path path) throws IOException {
        if (!Files.exists(path)) {
            Path parent = path.getParent();

            createDirectoryRecursively(parent);
            Files.createDirectory(path);
        }
    }

    private static List<String> getListFromString(final String input) {
        List<String> list = new ArrayList<>();

        if (input.contains(";")) {
            var elements = input.split(";");

            for (int index = elements.length - 1; index >= 0; index--) {
                if (!elements[index].isBlank()) {
                    list.add(elements[index]);
                }
            }
        } else if (!input.isBlank()) {
            list.add(input.trim());
        }

        return list;
    }

    private static void addPackageDependencies(JamCityPackage.JamCityPackageBuilder builder,
                                               Collection<String> dependencies, JamCityPackage.DependencyScope scope) {
        final Pattern pattern = Pattern.compile("^\\s*([\\w.]+)\\s*([<>=]+\\s*[\\d.]+\\s*)+$");

        for (String dependency : dependencies) {
            final Matcher matcher = pattern.matcher(dependency);

            if (!matcher.find()) {
                throw new IllegalArgumentException(String.format("Invalid dependency: %s", dependency));
            }

            String name = matcher.group(1);
            String version = matcher.group(2);

            builder.dependency(name, version, scope);
        }
    }
}
