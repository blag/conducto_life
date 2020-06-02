# Notes on Explaining Conducto

This file is mostly pre-writing.  Unless you're interested in *why* [README.md](README.md) looks the way it does, consider just moving on to that page.

...If you're still here, I'm sorry to have gone on at such length.  I didn't have time to be brief.

## First Impressions

I started my journey with Conducto on this page:
https://medium.com/conducto/introduction-to-conducto-pipelines-2759ecf876a2

First impressions only happen once, so I took some notes...

####  No module named 'conducto'

Consider adding `pip install conducto` to the first code block.

#### --local?

I see this was mentioned later, but up front It wasn't clear what `--local` was going to do.
I was suprised when it had something to do with opening a browser to a page not hosted locally.

After seeing that co.main() probably calls argparse (or similar), I tried `python demo.py --help` which didn't help.
Maybe add help strings to those parameters?

#### A Security Worry

It looks like I'm using a UI hosted by conducto to control docker containers running locally.
Something must be maintaining a persistent connection to conducto's servers....

    root@conducto_manager_qbe-lph:/usr/conducto# netstat -nputw
    Active Internet connections (w/o servers)
    Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name
    tcp        0      0 172.20.0.2:58604        3.12.66.255:443         ESTABLISHED 1/python

...and that container can create other containers, so it probably has access to the docker socket...

    ❯ docker inspect 4299748f360a  | grep '/var/run/docker.sock'
                    "/var/run/docker.sock:/var/run/docker.sock"
                    "Source": "/var/run/docker.sock",
                    "Destination": "/var/run/docker.sock",

...which can be used to act on the host filesystem as root (https://blog.secureideas.com/2018/05/escaping-the-whale-things-you-probably-shouldnt-do-with-docker-part-1.html).

I'm not worried myself--this seems like a necessary evil given what we're trying to do.
I'm worried that it will be percieved as a back door which leaves your system open to remote control by the contucto servers (or *any* servers, given a successful DNS poisoning).
As barriers to adoption go, there's nothing quite like a security-minded IT person acting like a hero because they've found something that they thought was hidden.
I think this could cause such an alarm.

It's probably at least worth considering ways to describe this on our terms.
This should happen pretty early in the onboarding process to protect new users from overzealous IT folk that might later stand between them and using Conducto.

#### A Dependency Worry

I ran across [a case](https://github.com/conducto/conducto/issues/3) where I couldn't talk to conducto.com.  Maybe it is possible to carry on development using just the cli, or to host something locally, but it wasn't apparent--so I was dead in the water.  Are we planning to support a free conducto-not-in-the-loop workflow?  If not then I fear that having the edit-run-pray loop depend on conducto.com might turn newcomers away.

## A Plan Emerges

The "Intro to Conducto Pipelines" post above occasionally uses words like 'simple' and 'easy'.
I don't doubt that once you know the ropes, writing a pipeline in conduco is easy.
And I won't argue that the interface isn't simple.
But there is a significant serving of complexity to be digested almost immediately upon starting to use Conducto for the first time.

So I would propose we create space for that complexity to sink in and defer the "first steps" for a second post.
Let's convince them to that walking through a "hello world" is a good idea, rather than just assuming that they're already game.

#### An introduction to Conducto should...

##### Establish the computational pipeline as a first-class citizen

Conducto is a general purpose solution in a space with many purpose-built solutions.
So let's make the alternatives look like "just a CI tool" or "just a science tool" and try to hook users that currently only have an inkling that a pipeline is what they need.
Such a user would be here because they're weighing these alternatives:

 - Custom GUIs
   - supports nontechnical users
   - high setup cost
   - high maintenance cost
   - dependency management: restricted to language ecosystem
   - time-granulaity: page view
   - data views: customizable

 - Traditional IDEs
   - low setup cost
   - discourages custom data views
   - time-granulaity: breakpoint
   - dependency management: restricted to language ecosystem
   - data views: not custom (debug tools)

 - Shells/REPLs
   - time-granulaity: command execution
   - low setup cost
   - dependency management: on your own
   - data views: on your own

 - Pipelines
   - middling setup cost
   - low maintenance cost
   - dependency management: flexible
   - time-granulaity: node (flexible)
   - data views: customizable

##### Showcase its strengths

They wouldn't be on this page unless maybe a pipeline solves their problem, but we should reassure the user that they're looking in the right place by showing Conducto being actually useful.

The example usage should be something that would be messier if done via a Conducto alternative (Lazy Node Placement maybe?)

##### Lean on User Expertise

If the first shown usage of Conducto is nontrivial, then whatever complexity it contains should be:

   - Familliar to both the data science crowd, the CI/CD crowd, and the new-to-pipelines crowd
   - Documented elsewhere
   - Fun to look at

I propose that we run Conway's Game of Life via a pipeline.
The last node can create an animated gif, and intermediate nodes can show the grid at each frame, rules can be applied in parallel.

##### Give a sense of what's going on under the hood

It took a moment to realize that the web GUI was controlling the docker daemon on my local machine.
Until that happened I was a bit bewildered.  This section can be short, a diagram and a sentence or two, but without knowing the basic setup it will be hard for users to right themselves if they've erred.
