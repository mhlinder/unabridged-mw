
This script fetches, parses, and displays dictionary entries from the
Unabridged Merriam-Webster website. The entries are formatted as plain
text for display in a terminal.

# Authentication

The Unabridged Merriam-Webster is subscription-based, and requires a
login to access dictionary content. Login credentials for your account
should be stored in `secret.py` as a function returning a 2-element
list:

```Python
def auth():
    return ('email@domain.com', 'Pa$$w0rd')
```

# Emacs

The function below prompts for a word, executes `mw.py`, and displays
the output in a new buffer.

```emacs
(defun mw ()
  (interactive)
  (let ((word (read-from-minibuffer "Lookup word: ")))
    (let ((buffname (format "*m-w: %s*" word))
          (cmd (format "mw.py %s" word)))
      (with-output-to-temp-buffer  buffname
        (shell-command cmd
                       buffname
                       "*Messages*")
        (pop-to-buffer buffname)))))
```
