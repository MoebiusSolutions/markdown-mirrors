markdown-mirrors
================

Overview
----------------

This utility is used to generate "mirror" pages in my standard markdown git repos.
These are pages that live in parallel with the main pages,
and link directly to the page within each of the parallel git mirrors.


Configuration
----------------

Copy `mirrors.yml.template` to your markdown repository, as `mirrors.yml`.

Modify the `mirrors` object in `mirrors.yml` to match your repository configurations.


Usage
----------------

Build the docker/podman image:

    cd ~/path/to/markdown-mirrors/

    docker build -t markdown-mirrors:local-build -f docker/Dockerfile .

Create a `markdown-mirrors.sh` script to launch the container.
Here is a good example, but yours may vary (docker vs podman, rootless vs rootful, etc):

    #!/bin/bash

    docker run --rm -it \
        `# Mount your input/output directory` \
        -v "$PWD/:/markdown/" \
        `# ... with minimal SELinux effects` \
        --security-opt label=disable \
        `# Generate new files with the ownership of the host user` \
        --user "$(id -u):$(id -g)" \
        `# The container has no need for network access` \
        --net none \
        markdown-mirrors:local-build \
        "$@"

Generate the "mirror" files:

    cd ~/path/to/markdown-repo/

    markdown-mirrors.sh /markdown/mirrors.yml generate /markdown/

Inject links to the "mirror" files to your existing markdown files:

    cd ~/path/to/markdown-repo/

    markdown-mirrors.sh /markdown/mirrors.yml add_header /markdown/


Developer Usage
----------------

If we need to update the `Pipfile` and `Pipfile.lock` with new dependencies,
we can enter a python container with this:

    cd ~/path/to/markdown-mirrors/

    docker run --rm -it \
        `# Mount the source directory` \
        -v "$PWD/:/opt/app/" \
        `# ... with minimal SELinux effects` \
        --security-opt label=disable \
        `# Generate new files with the ownership of the host user` \
        --user "$(id -u):$(id -g)" \
        --entrypoint /bin/bash \
        markdown-mirrors:local-build

... and from within the contianer, we can update the dependencies:

    pipenv install jinja2

At this point you would want to rebuild the image (per above)
