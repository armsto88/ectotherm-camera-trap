# Libraries downloaded from the registry are built without warnings, so that -Werror holds the
# project's own code to its standard without failing on code that is not ours to change.
Import("env")


def quiet(env, node):
    return env.Object(node, CCFLAGS=env["CCFLAGS"] + ["-w"])


env.AddBuildMiddleware(quiet, "*/libdeps/*")
