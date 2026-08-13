# External process and session custody

Load this reference when the maintained system starts, controls, times out, cancels, or
hands off an external command, worker, kernel, service, shell session, or other process.
It applies to local and remote sessions. The mechanisms below are examples of a custody
contract, not a requirement to use one operating system or supervisor.

## Proof target

The operation's owner remains able to identify and control the work it started. Record,
before launching work when possible:

- an owner or operation token and the session/transport handle;
- the exact command or request, start time, and monotonic operation deadline;
- the canonical workspace or execution root used by the command;
- the leader identity and the process-group, job, session, container, or supervisor
  identity that contains descendants;
- the owned descendant, pipe, socket, file, and other handle scope needed for cleanup;
- the teardown budget and the person or component responsible for the final watch.

Do not treat a user-facing timeout, a closed client connection, or a leader exit as proof
that the owned work stopped. A timeout is an observation that starts bounded cleanup.

## Capture identity before control

Create the containment scope before spawning where the platform permits. Immediately after
spawn succeeds, and before cancellation or a wait, capture one custody record containing
the owner token, a leader handle or PID plus start-time identity, and the process-group,
job, session, container, or supervisor identity. Treat that record as immutable for the
operation. Never reconstruct a kill scope from a late PGID read after the leader exits or
changes groups. If an immutable handle or PID-plus-start identity cannot be captured,
do not guess from a process name or late PGID: preserve the launch evidence, use a
pre-established supervisor boundary if available, and report `runtimeObserved: NOT_PROVEN`
until exact ownership and cleanup can be proven.

## One operation, one live custody

Use a monotonic operation deadline for the requested work and a separate, named monotonic
teardown budget for stopping and reaping it. Keep the same live session and checkpoint
identity while diagnosing or cleaning up. Never start a duplicate command merely because
the first call timed out or its output was incomplete. A replacement or new writer may
start only after the original custody is proven stopped and reaped, or
`runtimeObserved: NOT_PROVEN` is recorded with a named owner and safe recovery path.

## Exact-scope teardown

For a timeout, cancellation, launch failure, or parent shutdown, perform one bounded
teardown sequence against the recorded ownership scope:

1. stop accepting input and close the owned stdin/command channel;
2. request a graceful termination signal for the exact leader and its owned group/job/
   session/supervisor scope;
3. wait only within the grace portion of the teardown budget;
4. force-stop the same exact scope if it remains live;
5. wait and reap the leader with a bounded wait, then drain or close owned output pipes;
6. prove that no owned descendant, group/job member, session, or cleanup handle remains;
7. record the observation and perform a post-watch after the teardown budget.

Use an ownership token, process handle, start-time check, or equivalent identity check to
avoid PID reuse. Never kill by a broad process name, an unverified PID, or a group that may
contain unrelated work. If exact-scope membership or reaping cannot be proved, stop
claiming success and report `runtimeObserved: NOT_PROVEN` with the remaining evidence;
use the method's `PARTIAL` or `BLOCKED` status when no safe recovery remains.

## Parent-death and containment

Parent cleanup code cannot run after an ungraceful parent death. A process group, job,
session, container, or cgroup is a containment scope; it does not by itself observe that
the owner disappeared. Where the platform allows, pair that scope with a
supervisor/guardian, job-close rule, parent-death hook, subreaper, liveness pipe, or
equivalent mechanism that observes owner disappearance and runs the same bounded teardown.
A mechanism that only sends a signal to the leader is insufficient when descendants can
keep pipes, sockets, or work alive.

Prefer the strongest boundary available to the deployment. A portable fallback may be
valid for a non-adversarial environment, but state what it cannot contain (for example,
daemonization outside the recorded scope) and downgrade the result when that limitation
matters.

## Evidence and watch

At each checkpoint and in the final result, retain the command/session token, canonical
workspace identity, leader and group/job identity, deadline and teardown budget,
signal/wait sequence, reap result, and no-survivor observation. Include whether output
pipes reached EOF and whether generated logs, sockets, temporary files, or caches were
cleaned without touching unrelated data.

The minimum regression set covers:

- a timeout where a shell starts a background child;
- a leader that exits while a descendant still holds an output pipe;
- cancellation during startup and during active work;
- parent death or transport loss;
- a PID-reuse/name-collision attempt and a child that starts near teardown;
- a failed launch and a handoff attempt before reaping.

Run a bounded immediate check and a delayed post-watch. If a survivor is found, preserve
its identity and evidence, execute only the remaining exact-scope cleanup, and keep
`runtimeObserved: NOT_PROVEN` until the contract is re-established.
