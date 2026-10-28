# Secrets

- Live secrets sit next to the services that read them: `.env` files, key
  files, token and credential files, and each tool's own login files. Never
  print, quote, summarize or commit them, and don't open them. If you need
  to know whether one is set, check only that the file exists, or ask the
  user.
- Before committing, check that no secret file is staged. Don't widen a
  `.gitignore` to include one.
- If you find a secret somewhere it shouldn't be (in git, a log, a doc),
  tell the user. Don't move or delete it yourself.
