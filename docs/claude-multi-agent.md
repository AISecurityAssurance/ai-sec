https://javascript.plainenglish.io/i-built-an-ai-team-that-codes-itself-and-you-can-too-974a48b4ef49


I Built an AI Team That Codes Itself, And You Can Too
No prompts. No babysitting. Just real coding agents, building full-stack apps while you sleep.

Months ago, I thought AI coding agents peaked with tools like Cursor and Claude Code.

Then something wild happened.

I discovered a way to turn a single Claude Code instance into an autonomous software engineering team, project managers, frontend devs, backend devs , all running simultaneously, all following deadlines, all committing code without my input.

They don’t wait for me. They don’t need approvals. They don’t ask permission.

They just build.

Let me show you how it works, and why this might be the future of AI development.

The Backstory: From AI Helpers to Autonomous Systems
Over the past year, we’ve seen AI coding assistants evolve rapidly:

Cursor turned VS Code into a co-pilot.
Claude Code gave us smart terminals that actually understand context.
Agentic workflows became buzzwords.
But all of them had one thing in common:
They still needed you to click approve.

What I discovered today flips that on its head.

I set up a system that doesn’t just run Claude Code, it orchestrates multiple Claude agents working in parallel. On their own.

These agents collaborate across different terminals, check in on each other’s work, and follow a strict schedule, all without me lifting a finger.

Let me show you exactly how it works.

What the Tmux Orchestrator Actually Does
Welcome to the Tmux Orchestrator, a framework that turns Claude Code into a self-governing, always-on software team.

It’ more than just a clever script. It’s an architectural framework that:

Runs Claude agents 24/7, while you sleep.
Schedules its own check-ins and reassigns work autonomously.
Coordinates multiple engineers and project managers across different projects.
Scales infinitely by spawning parallel teams inside tmux windows.
Persists work even when your terminal is closed or laptop is shut.
Imagine Cursor… but it builds your app without needing you to hold its hand.

If you haven’t set up Claude Code on your machine, you’ll need it before running the orchestrator, I’ve written a step-by-step guide that walks you through the full setup.

The Breakthrough: Tmux Orchestrator
The magic happens through a GitHub repo called Tmux Orchestrator.

This framework turns your terminal into a self-managing AI development environment.

Here’s What It Does:
Launches a master Claude agent.
That master agent spawns sub-agents in new terminals.
Each sub-agent is assigned a role (e.g., frontend developer, backend PM).
Agents follow a detailed spec and stick to a strict timeline.
Progress is auto-tracked, committed, and checkpointed.
And yes, it works. Really well.

How It Works: The Three-Tier Agent Hierarchy
To overcome context limitations, the orchestrator uses a tiered agent hierarchy:


┌─────────────┐
│ Orchestrator│ ← You interact here (once)
└──────┬──────┘
       │ Monitors & coordinates
       ▼
┌─────────────┐     ┌─────────────┐
│  Project    │     │  Project    │ ← Assign tasks, enforce specs
│  Manager 1  │     │  Manager 2  │
└──────┬──────┘     └──────┬──────┘
       │                   │
       ▼                   ▼
┌─────────────┐     ┌─────────────┐
│ Engineer 1  │     │ Engineer 2  │ ← Write code, fix bugs, run tests
└─────────────┘     └─────────────┘
Each layer has a narrow focus and clean responsibilities, keeping agents within manageable context windows.

Orchestrator oversees all projects
Project Managers enforce specifications, timelines, and coordination
Engineers write code, test, and commit
Step-by-Step: How to Build Your Own AI Dev Team
Let me break down the full setup so you can try it yourself.

Step 1: Clone the Framework
Navigate to your target directory.
Clone the repo:
git clone https://github.com/Jedward23/Tmux-Orchestrator.git
cd Tmux-Orchestrator
3. Run the provided setup scripts to make files executable.

Step 2: Start a New Tmux Session
Create a new session (e.g. my-agent) and keep it open.

tmux new-session -s my-agent

Step 3: Enable Autonomy with a Critical Flag (Optional)
Now you can run Claude Code.

If you want Claude to execute commands without stopping for your approval you can replace:

claude
with:

claude --dangerously-skip-permissions-check
Zoom image will be displayed

The Spec Folder: Your New Source of Truth
To guide your agents, you’ll create a folder with multiple spec files:

main_spec.md: the big picture
frontend_spec.md: includes UI reference images and implementation plans
backend_spec.md: API design, database schemas, and logic
integration_spec.md: how everything fits together across teams
These files act like product requirement docs that your agents follow to build the full app.

You can ask claude to help you generate those.

Here’s an example of a template:

PROJECT: E-commerce Checkout  
GOAL: Implement multi-step checkout

CONSTRAINTS:
- Use existing cart state
- Follow design system
- Max 3 API endpoints
- Commit after each step
DELIVERABLES:
1. Shipping form w/ validation  
2. Payment method selection  
3. Order confirmation page  
4. Success/failure handling
SUCCESS CRITERIA:
- Forms validate
- Payment succeeds  
- DB stores order  
- Emails trigger
You can even specify deadlines and resource allocation across teams.

The Most Important File You’re Not Using Yet: prompt.md
While the spec.md files define what your project should look like, the prompt.md file tells the orchestrator how to manage the build process.

Think of it as the mission briefing for your AI project manager. Without it, agents know what to build, but not how to coordinate.

Here’s an example of a prompt.md:
The specs are located in ~/Projects/EcommApp/Specs.

Create:
- A frontend team (PM, Dev, UI Tester)
- A backend team (PM, Dev, API Tester)
- An Auth team (PM, Dev)
Schedule:
- 15-minute check-ins with PMs
- 30-minute commits from devs
- 1-hour orchestrator status sync
Start frontend and backend on Phase 1 immediately. Start Auth on Phase 2 kickoff.
You can edit your own prompt.md by adjusting:

The path to your Spec folder (~/projects/EcommApp/Spec in the example)
The number and type of teams (Frontend, Backend, Auth, Analytics, QA, etc.)
The commit rhythm (every 30 minutes is ideal for Git traceability)
Phase control (Start all at once, staggered, or conditional on success)
Then hit go.

What Happens After You Run Claude: Agents, Teams & Terminal Coordination
Once you’ve launched your orchestrator with prompt.md and your spec files in place, Claude takes over, and this is where the magic begins.

Here’s what Claude does next:
Parses your prompt.md
It identifies what teams to create (e.g., Frontend, Backend), where the specs live, and how to coordinate timing.
Spins up tmux windows for each role:
Frontend Project Manager
Frontend Developer
Frontend Server (for tests/builds)
Backend Project Manager
Backend Developer
Backend Server
Orchestrator (you)
Shared Logging/Check-ins
Assigns responsibilities
Each agent gets a job based on the specs and the instructions in prompt.md.
Starts Phase 1 for all teams
If you’ve requested simultaneous launch, every team kicks off at once.
Schedules self-checks every 15 minutes
These check-ins track progress, review commits, and move each team to the next phase if ready.
Here’s what a typical project might look like on disk. Think of this as the “brain” Claude reads from:

~/Projects/EcommApp/
│
├── prompt.md                  # High-level instructions for orchestrator
├── Specs/
│   ├── main_spec.md           # Timeline and global goals
│   ├── frontend_spec.md       # UI requirements, components, mockups
│   ├── backend_spec.md        # API endpoints, DB logic
│   ├── integration_spec.md    # How front + back sync together
│
├── UI_Reference/
│   ├── design.png             # Screenshot or figma export
│   └── implementation.md      # Step-by-step ShadCN component plan
│
├── TaskManager/
│   └── (Generated Code)       # Claude will build your app here
│
├── Claude_Scripts/
│   ├── send-claude-message.sh
│   ├── schedule_with_note.sh
│   └── tmux_utils.py
Important: Always use absolute paths in your prompt.md so Claude doesn’t get lost.

And Now in Your Terminal…
Once the orchestrator runs, you’ll see something like this in your tmux session:

┌───────────────────────────────┐
│ orchestrator:0                │ ← You (control tower)
├───────────────────────────────┤
│ frontend-pm:1                 │ ← Reads frontend_spec.md
│ frontend-dev:2                │ ← Builds UI, pushes commits
│ frontend-server:3             │ ← Runs tests, previews UI
├───────────────────────────────┤
│ backend-pm:4                  │ ← Assigns tasks from backend_spec.md
│ backend-dev:5                 │ ← Builds APIs, fixes bugs
│ backend-server:6              │ ← Runs backend tests, logs results
├───────────────────────────────┤
│ status-logger:7               │ ← Check-ins every 15 mins
└───────────────────────────────┘
Zoom image will be displayed
Each of these panes is a fully autonomous Claude agent, receiving instructions, reading specs, writing code, and reporting status.

It’s like having a fully staffed sprint team working inside your terminal, no hand-holding needed.

Final Thoughts: The Future of Coding Just Got a Lot Weirder
When I first imagined autonomous AI agents, I thought:
Someday.

Now?
I’ve got eight of them running in my terminal right now, coding, debugging, and checking each other’s work.

No plugins. No IDE bloat. Just terminals, specs, and coordination.

This isn’t the end of developers. But it is the beginning of something wild:

Code as orchestration. Engineering as prompt design.

The tools are here. The future’s already running.