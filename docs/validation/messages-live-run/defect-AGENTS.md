# Mailbox

`.sdlc/messages/` is the mailbox for this repository. Messages arrive in `new/<receiver>/`.

## Handle a message you were given

1. Print it: `cat <path>`. `<path>` is the path you were given.
2. Move it to the done folder: `mkdir -p .sdlc/messages/done/<receiver> && mv <path> .sdlc/messages/done/<receiver>/`. `<receiver>` is the folder after `new/`. Run this from the repository root.

That is all. No reply is needed, and no script is needed.
