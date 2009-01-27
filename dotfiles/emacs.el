;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;                                                                ;
;   yet another .emacs file / last edited by tav on 2004/11/18   ;
;                                                                ;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

; to set-fill-column
; use M-<number> C-x f

(setq user-full-name "tav")
(setq user-mail-address "tav@espians.com")

  (defun mac-insert-hash () 
    "Insert a hash / octothorp character"
    (interactive)
    (insert-char ?# 1))

  (define-key global-map "\M-3" 'mac-insert-hash)

;
; load the various packages installed through gentoo
;

; (load "/home/tav/.site-lisp/site-gentoo")

; (pc-selection-mode)
(setq mac-command-key-is-meta nil)
; (setq mac-command-modifier 'meta)

;
; find out which of the evil twins we are using
;

(defvar running-xemacs
  (string-match "XEmacs\\|Lucid" emacs-version)
  "are we running xemacs?")

;
; provide some utility macros
;

(defmacro safe-exec (&rest body)
  "safely execute body, return nil if an error occurred"
  (` (condition-case nil
	 (progn (,@ body))
       (error nil))))

(defmacro GNUEmacs (&rest x)
  (list 'if (not running-xemacs) (cons 'progn x)))

(defmacro XEmacs (&rest x)
  (list 'if running-xemacs (cons 'progn x)))

(defmacro Xlaunch (&rest x)
  (list 'if (eq window-system 'x) (cons 'progn x)))

;
; nicer shell support in emacs
;

(add-hook 'comint-output-filter-functions 'shell-strip-ctrl-m)
(add-hook 'comint-output-filter-functions 'comint-watch-for-password-prompt)

;
; turn on syntax highlighting
;

(global-font-lock-mode)
(setq font-lock-maximum-decoration t)

;
; want a final newline? use non-nil but not t to ask whether to add one
;

(setq require-final-newline "ask me")
(setq require-final-newline nil)

;
; graphically display the region between the point and mark when C-x C-x
;

(transient-mark-mode 1)

;
; set us up a visible bell
;

(setq visible-bell t)

;
; ring the bell when you try to move down below the last line of the buffer
;

(setq next-line-add-newlines nil)

;
; ascii?!? pfft! always encode to utf-8 when saving
;

; (set-default-coding-systems 'mule-utf-8)
(set-language-environment 'utf-8)

;(add-hook 'write-file-hooks
;          (lambda ()
;            (set-buffer-file-coding-system 'mule-utf-8 t)
;            nil))

;; (set-buffer-file-coding-system 'iso-8859-1-unix t)
;; (setq current-language-environment "ASCII")
;; (set-language-environment 'Polish)
;; (default-input-method "rfc1345")
;; (set-input-method 'latin-2-prefix)

;
; transparent compression support for .gz, .Z, .tgz, .bz2
;

(require 'jka-compr) 

(auto-compression-mode t)

;
; get rid of the menu bar in terminal mode
;

(if (equal window-system nil)
    (menu-bar-mode nil))

;
; get rid of all the annoying graphical fluff
;

; (menu-bar-mode nil)
(tool-bar-mode nil)
(scroll-bar-mode nil)

;
; and, bye bye startup fluff
;

(setq inhibit-startup-message t)

;
; display current line and column number? fuck yes!
;

(column-number-mode t)
(line-number-mode t)

;
; useful to display current time too
;

;; (setq display-time-24hr-format t)
;; (setq display-time-day-and-date t)

(setq display-time-format "%H:%M")
(display-time)

;
; set the current buffer's filename, and full path in the titlebar
;

(setq frame-title-format '("%b" (buffer-file-name ": %f")))

;
; specify the location and size of the initial emacs frame
;

(if window-system
    (setq default-frame-alist
	  '((wait-for-wm . nil)
 	    (top . 26) (left . 840)
 	    (width . 117) (height . 62)
;	    (background-color . "gray15")
;	    (foreground-color . "limegreen")
	    (cursor-color . "LightGoldenrod")
	    (mouse-color . "yellow")
		(alpha . 80)
	    ))

;   (setq initial-frame-alist 
; 	'((top . 20) (left . 3-th)
; 	  (width . 80) (height . 33)
; 	  ))

)

;
; colour themes ++
;


(add-to-list 'load-path "/Users/tav/.site-lisp/")
(add-to-list 'load-path "/home/tav/.site-lisp/color-theme")

(require 'color-theme)

;; (color-theme-arjen)
;; (color-theme-blue-mood)
;; (color-theme-charcoal-black)
;; (color-theme-clarity)
;; (color-theme-comidia)
;; (color-theme-goldenrod)
;; (color-theme-hober)
;; (color-theme-lawrence)
;; (color-theme-ld-dark)
;; (color-theme-matrix)

(setq color-theme-is-global t)

;
; highlight them parentheses -- perhaps checkout mic-paren
;

(show-paren-mode t)

;
; search and replace highlighting
;

(setq search-highlight t)
(setq query-replace-highlight t)

;
; interpret line breaks as ordinary spaces in incremental search
;

(setq search-whitespace-regexp "[ \t\r\n]+")

;
; ignore case when searching
;

(setq case-fold-search t)

;
; bye bye evil tabs!
;

(setq default-tab-width 4)
(setq indent-tabs-mode nil)

(setq c-mode-hook
	  (function (lambda ()
				  (setq indent-tabs-mode nil)
				  (setq c-basic-offset 4)
				  (setq c-indent-level 4))))

;
; accept 'y' and 'n' instead of requiring 'yes'/'no'
;

(fset 'yes-or-no-p 'y-or-n-p)

;
; treat enter as a yes too
;

;; (define-key query-replace-map [return] 'act)

;
; ask for confirmation before quiting emacs
;

(if window-system
    (setq confirm-kill-emacs 'y-or-n-p))

;; (global-unset-key "\C-x\C-c")

;
; append to our path of executables
;

(setq exec-path (cons "/usr/local/bin" exec-path))

;
; .emacs
;

(defun dot-emacs() "open my .emacs" (interactive)
  (find-file "~/.emacs"))

;
; that default pager so horrible. use this instead!
;

(add-to-list 'load-path "/home/tav/.site-lisp/pager")
(require 'pager)

(global-set-key [next] 'pager-page-down)
(global-set-key [prior] 'pager-page-up)

;; cant use non-ascii in terms it seems -- also whats with the leading ' ? --
;; can use more than first 127 ascii when using vectors instead of strings --
;; here, we explore different ways of setting keybindings -- see bindings.el

(global-set-key '[M-down] 'pager-row-down)
(global-set-key '[(meta up)] 'pager-row-up)

;; (global-set-key [(ctrl v)] 'pager-row-down)
;; (global-set-key [(meta v)] 'pager-row-up)

(define-key esc-map [down] 'pager-row-down)
(define-key esc-map [up] 'pager-row-up)

;
; move to the start/end of braces -- already bound to C-M-b and C-M-f for terms
;

(global-set-key [(meta left)] 'backward-sexp)
(global-set-key [(meta right)] 'forward-sexp)

(define-key esc-map [left] 'backward-sexp)
(define-key esc-map [right] 'forward-sexp)

;
; goto!
;

(global-set-key [(meta g)] 'goto-line)

;
; cycle through the windows
;

(global-set-key "\C-n" 'other-window)

;
; cycle through the buffers
;

(global-set-key [C-tab] 'bs-cycle-next)
(global-set-key [S-tab] 'bs-cycle-previous) 

;; @/@ above S-tab no workie

(define-key esc-map "n" 'bs-cycle-previous)

;; (setq bs-cycle-configuration-name "all")

;
; buffer save/revert -- @/@ find good keybindings
;

;; (global-set-key "\C-O" 'save-buffer)
;; (global-set-key "\C-x\C-a" 'revert-buffer)

(global-set-key "\C-k" 'kill-buffer)

;
; sanity check!
;

(global-set-key [home] 'beginning-of-line)
(global-set-key [end] 'end-of-line)

(define-key global-map [home] 'beginning-of-line)

;
; override default tags keybindings with begin/end of buffers
;

(global-set-key '[(meta ,)] 'beginning-of-buffer)
(global-set-key '[(meta .)] 'end-of-buffer)

;
; delete away
;

(global-set-key [delete] 'delete-char)
(global-set-key [backspace] 'delete-backward-char)

(global-set-key [(control backspace)] 'backward-kill-word)
(global-set-key [(control delete)] 'kill-word)

(setq kill-whole-line t)

;
; remap quoted-insert -- for inserting literal characters / control characters
;

(global-set-key [?\C-c ?q] 'quoted-insert)

;
; undo in the familiar setting -- although C-/ and C-_ is easier on the fingers
;

;; (global-set-key "\C-z" 'undo)
;; (global-set-key [(meta backspace)] 'undo)

;
; comment/uncomment regions
;

(global-set-key [?\C-c ?c] 'comment-region)
(global-set-key [?\C-c ?u] 'uncomment-region)

;
; function key powah!
;

(global-set-key [f1] 'man-follow)
(global-set-key [f2] 'server-start)
(global-set-key [f3] 'buffer-menu)
(global-set-key [f4] 'desktop-save)
(global-set-key [f5] 'time-stamp)
(global-set-key [f6] 'speedbar-get-focus)
; (global-set-key [f7] 'ispell-minor-mode)
;; f8
(global-set-key [f9] 'make-frame-on-display)
;; f10 -- menu
(global-set-key [f11] 'delete-other-windows)
;; f12

(define-key esc-map [f7] 'flyspell-mode)
(global-set-key [M-f7] 'flyspell-mode)
(global-set-key [C-f7] 'flyspell-prog-mode)

;
; seeing as we overwrite the binding below, we bind it to another key
;

(global-set-key "\C-c " 'just-one-space)

;
; auto-complete! @/@
;

;; 'dabbrev-expand is by default bound to M-/

;; (global-set-key [M-return] 'expand-abbrev)
;; (global-set-key [M-return] 'dabbrev-expand)

(require 'hippie-exp)

(global-set-key "\M- " 'hippie-expand)
(define-key esc-map " " 'hippie-expand)

(setq hippie-expand-try-functions-list
;;	  '(try-complete-file-name-partially
;;		try-complete-file-name
	  '(try-expand-all-abbrevs
		try-expand-list
;;		try-expand-line
		try-expand-dabbrev
		try-expand-dabbrev-all-buffers
		try-expand-dabbrev-from-kill))
;;		ispell-complete-word))

;; (fset 'my-hippie-expand (make-hippie-expand-function
;; 						 '(try-complete-file-name-partially
;; 						   try-complete-file-name
;; 						   try-expand-all-abbrevs
;; 						   try-expand-list
;; 						   try-expand-line
;; 						   try-expand-dabbrev
;; 						   try-expand-dabbrev-all-buffers
;; 						   try-expand-dabbrev-from-kill
;; 						   try-complete-lisp-symbol-partially
;; 						   try-complete-lisp-symbol
;; 						   ispell-complete-word)))

;; (global-set-key "\M- " 'my-hippie-expand)
;; (define-key esc-map " " 'my-hippie-expand)

;
; spell-checking and auto-complete
;

; (setq ispell-dictionary "british")
; (setq ispell-local-dictionary "british")

;; complete-word uses alternate dictionary, e.g. /usr/share/dict/words
; (define-key esc-map "p" 'ispell-complete-word)

; (global-set-key [?\C-p] 'ispell-word)

;; silently save personal dictionary
; (setq ispell-silently-savep t)

;
; @/@ -- download ehm, if using decent parens package...
;

;; (global-set-key "%" 'match-paren)

;
; open a file
;

(global-set-key "\C-O" 'find-file)

;
; webdav support! (C-x C-f :http://your.webdav.server:port/path/to/file/name)
;

; (setq load-path (cons "/home/tav/.site-lisp/eldav/" load-path))

; (require 'eldav)

;; uncomment the following to enable version control support
;; (setq eldav-use-vc t)

;
; ange-ftp-over-ssh power!
;

(setq ange-ftp-ftp-program-name "nftp.pl")

;
; the wonders of backup
;

;; @/@ -- download
;; (require 'backup-dir) 
;; (setq bkup-backup-directory-info 
;;       '((t "/home/tav/.backups" ok-create full-path))) 

(setq backup-directory-alist '(("." . "~/.emacs_backups")))

;
; version numbers for backup files
;

(setq version-control t)

(setq kept-old-versions 3)
(setq kept-new-versions 3)

(setq delete-old-versions t)

;
; @/@ -- ?? templating power
;

;; (setq template-home-directory "/home/tav")

(require 'tempo)
(global-set-key [?\C-c ?t] 'tempo-template-to-string-method)

;; look at html-helper-mode.el in /var/dev/snippets for guidance on this...

;
; bookmark it!
;

(setq bookmark-default-file "~/.emacs.bookmarks")
(setq bookmark-save 1)
(setq bookmark-version-control "nospecial")

(global-set-key [?\C-c ?j] 'bookmark-jump)
(global-set-key [?\C-c ?e] 'bookmark-set)
(global-set-key [?\C-c ?r] 'bookmark-rename)

;
; extend that load-path
;

(setq load-path
      (append load-path
	      (list
	       "/home/tav/.site-lisp/apel"
	       )))

;
; crypt++
;

; (add-to-list 'load-path  "/home/tav/.site-lisp/crypt++")

; (require 'crypt++)

;
; css-mode
;

(add-to-list 'load-path "/home/tav/.site-lisp/css-mode")
(add-to-list 'auto-mode-alist '("\\.css$" . css-mode))

(autoload 'css-mode "css-mode" "css editing mode" t)

;
; elib
;

(add-to-list 'load-path "/home/tav/.site-lisp/elib")

;
; erc
;

(add-to-list 'load-path "@SITELISP@")

(autoload 'erc-select "erc" "start erc" t)

;
; flim
;

(add-to-list 'load-path "/home/tav/.site-lisp/flim")

;
; javascript-mode
;

; (add-to-list 'load-path "/home/tav/.site-lisp/javascript-mode")
; (autoload 'javascript-mode "javascript-mode" "javascript editing mode" t)

(autoload 'js2-mode "js2" "javascript editing mode" t)
(add-to-list 'auto-mode-alist '("\\.js$" . js2-mode))

;
; nxml-mode
;

(add-to-list 'load-path "/home/tav/.site-lisp/nxml-mode")
; (load "/home/tav/.site-lisp/nxml-mode/rng-auto.el")

(add-to-list 'auto-mode-alist
	     '("\\.\\(xml\\|xsl\\|xsd\\|rng\\|kid\\|pyxt\\|xhtml\\)\\'" . nxml-mode))

(add-to-list 'auto-mode-alist
	     '("\\.\\(pt\\|zpt\\|genshi\\|html\\|zcml\\|rdf\\)$" . nxml-mode))

(autoload 'nxml-mode "nxml-mode" "nxml editing mode" t)

(define-key esc-map "o" 'nxml-complete)

(setq nxml-attribute-indent 4)
(setq nxml-child-indent 2)
(setq nxml-sexp-element-flag t)
(setq nxml-slash-auto-complete-flag t)

;; (defun my-nxml-mode-hook()
;;   (interactive)
;;   (add-to-list 'hippie-expand-try-functions-list 'nxml-complete))

;; (add-hook 'nxml-mode-hook 'my-nxml-mode-hook)

;
; ocaml-mode
;

(add-to-list 'load-path "/home/tav/.site-lisp/ocaml-mode/")
(add-to-list 'auto-mode-alist '("\\.ml[iylp]?$" . caml-mode))

(autoload 'caml-mode "caml" "ocaml editing mode" t)
(autoload 'run-caml "inf-caml" "run an ocaml toplevel" t)
(autoload 'camldebug "camldebug" "ocaml debug mode" t)

; (require 'caml-font)

;
; po-mode -- for editing gettext files
;

(add-to-list 'load-path "/home/tav/.site-lisp/po-mode/")
(autoload 'po-mode "po-mode" "po editing mode" t)

(add-to-list 'auto-mode-alist '("\\.po\\'\\|\\.po\\." . po-mode))

(autoload 'po-find-file-coding-system "po-compat")

(modify-coding-system-alist 'file "\\.po\\'\\|\\.po\\."
			    'po-find-file-coding-system)

;
; python-mode
;

(add-to-list 'load-path "/home/tav/.site-lisp/python-mode")
(add-to-list 'auto-mode-alist '("\\.py$" . python-mode))
(add-to-list 'auto-mode-alist '("SConscript" . python-mode))
(add-to-list 'auto-mode-alist '("SConstruct" . python-mode))
(add-to-list 'auto-mode-alist '("\\.py[xdi]?$" . python-mode))

;; @/@ -- merge following together
(add-to-list 'interpreter-mode-alist '("python" . python-mode))
(add-to-list 'interpreter-mode-alist '("python.recent" . python-mode))
(add-to-list 'interpreter-mode-alist '("python2.3" . python-mode))
(add-to-list 'interpreter-mode-alist '("python2.4" . python-mode))
(add-to-list 'interpreter-mode-alist '("python2.5" . python-mode))
(add-to-list 'interpreter-mode-alist '("python2.6" . python-mode))

;; (setq interpreter-mode-alist
;;       (append interpreter-mode-alist
;; 	      (list
;; 	       "python"
;; 		   "python.recent"
;; 		   "python2.3"
;; 		   "python2.4"
;; 	       )))

(autoload 'python-mode "python-mode" "python editing mode" t)

(setq py-smart-indentation t)
(setq py-python-command "python")
(setq py-jump-on-exception t)
(setq py-pdbtrack-do-tracking-p t)

(add-to-list 'auto-mode-alist '("\\.pyx\\'" . cython-mode))

(define-derived-mode cython-mode python-mode "Cython"
  (font-lock-add-keywords
   nil
   `((,(concat "\\<\\(NULL"
	       "\\|c\\(def\\|har\\|typedef\\)"
	       "\\|e\\(num\\|xtern\\)"
	       "\\|float"
	       "\\|in\\(clude\\|t\\)"
	       "\\|object\\|public\\|struct\\|type\\|union\\|void"
	       "\\)\\>")
      1 font-lock-keyword-face t))))

;; (add-to-list 'load-path "/home/tav/.site-lisp/ipython")
;; (require 'ipython)

;
; rst-mode
;

; (add-to-list 'load-path "/home/tav/.site-lisp/rst")
; (autoload 'rst-mode "rst-mode" "rst editing mode" t)
; (setq rst-mode-lazy nil)

(require 'rst)

(add-hook 'text-mode-hook 'rst-text-mode-bindings)

(add-to-list 'auto-mode-alist '("\\.txt$" . rst-mode))
(add-to-list 'auto-mode-alist '("\\.yaml$" . rst-mode))
(add-to-list 'auto-mode-alist '("\\.rst$" . rst-mode))
(add-to-list 'auto-mode-alist '("\\.jen$" . rst-mode))
(add-to-list 'auto-mode-alist '("\\.notes$" . rst-mode))

;
; let restructuredtext rule!
;

; (setq default-major-mode 'rst-mode)

(setq text-mode-hook
;;    (quote (turn-on-auto-fill text-mode-hook-identify)))
      (quote (flyspell-mode turn-on-auto-fill text-mode-hook-identify)))

(setq flyspell-default-dictionary "english")

;
; w3m -- web browsing in emacs! <g>
;

(add-to-list 'load-path "/home/tav/.site-lisp/emacs-w3m")

(autoload 'w3m "w3m" "w3m interface" t)
(autoload 'w3m-browse-url "w3m" "browse the web" t)
(autoload 'w3m-find-file "w3m" "browse local files" t)
(autoload 'w3m-search "w3m" "search QUERY using SEARCH-ENGINE" t)
(autoload 'w3m-weather "w3m" "get weather reports" t)
(autoload 'w3m=antenna "w3m" "monitor site changes" t)
(autoload 'w3m-namazu "w3m" "search files with namazu" t)

(setq w3m-icon-directory "/usr/share/emacs-w3m/icon")

;
; miscellaneous auto modes
;

;; (setq auto-mode-alist
;;      (cons '("changelog.txt" . change-log-mode) auto-mode-alist))

(setq auto-mode-alist
      (append
       (list
		'("changelog.txt" . change-log-mode)
		'("\\.htaccess$"   . apache-mode)
		'("httpd\\.conf$"  . apache-mode)
		'("srm\\.conf$"    . apache-mode)
		'("access\\.conf$" . apache-mode)
		) auto-mode-alist))

;
; ignore them pesky subversion directories
;

;; @/@ -- the directories one don't seem to work
(add-to-list (quote completion-ignored-extensions) "CVS/")
(add-to-list (quote completion-ignored-extensions) ".svn")

(add-to-list (quote completion-ignored-extensions) ".pyc")

;
; ignore case in completion too
;

(setq completion-ignore-case t)

;
; set a default "working directory"
;

;; (cd "/kalati/sandbox/tav/main/")
;; (cd "~/files")

;
; say hi!
;

(message "loading... done")

;; -------------------------------------------------------------------------

;;  '(desktop-enable t nil (desktop))
;;  '(uniquify-buffer-name-style nil nil (uniquify))

;; -------------------------------------------------------------------------

;; (font-lock-comment-face ((((type tty pc) (class color) (background dark) (:foreground "red" :weight bold))))
;; (font-lock-doc-face ((t (:foreground "white" :weight bold))))
;; (font-lock-function-name-face ((((type tty) (class color)) (:foreground "white" :weight bold))))
;; (font-lock-string-face ((((type tty) (class color)) (:foreground "green" :weight bold))))
;; (font-lock-type-face ((((type tty) (class color)) (:inherit font-lock-function-name-face :foreground "blue" :weight bold))))

(custom-set-variables
  ;; custom-set-variables was added by Custom -- don't edit or cut/paste it!
  ;; Your init file should contain only one such instance.
 '(ecb-options-version "2.24")
 '(global-font-lock-mode t nil (font-lock)))

(custom-set-faces
  ;; custom-set-faces was added by Custom -- don't edit or cut/paste it!
  ;; Your init file should contain only one such instance.
 '(font-lock-comment-face ((((type tty pc) (class color) (background dark)) (:foreground "red" :weight bold))))
 '(font-lock-doc-face ((t (:foreground "white" :weight bold))))
 '(font-lock-function-name-face ((((type tty) (class color)) (:foreground "white" :weight bold))))
 '(font-lock-string-face ((((type tty) (class color)) (:foreground "green" :weight bold))))
 '(font-lock-type-face ((((type tty) (class color)) (:inherit font-lock-function-name-face :foreground "blue" :weight bold))))
 '(nxml-attribute-colon-face ((t (:inherit nxml-attribute-local-name-face))))
 '(nxml-attribute-local-name-face ((t (:foreground "DarkSeaGreen"))))
 '(nxml-attribute-prefix-face ((t (:inherit nxml-attribute-local-name-face))))
 '(nxml-attribute-value-delimiter-face ((t (:inherit nxml-tag-delimiter-face))))
 '(nxml-attribute-value-face ((t (:foreground "LightSteelBlue"))))
 '(nxml-comment-content-face ((t (:foreground "Sienna1"))))
 '(nxml-comment-delimiter-face ((t (:inherit nxml-comment-content-face))))
 '(nxml-delimited-data-face ((((class color) (background light)) (:inherit nxml-name-face))))
 '(nxml-delimiter-face ((t (:inherit nxml-name-face))))
 '(nxml-element-colon-face ((t (:inherit nxml-element-local-name-face))))
 '(nxml-element-local-name-face ((t (:foreground "Darkseagreen"))))
 '(nxml-element-prefix-face ((t (:inherit nxml-element-local-name-face))))
 '(nxml-entity-ref-name-face ((t (:inherit nxml-ref-face))))
 '(nxml-markup-declaration-delimiter-face ((t (:inherit nxml-prolog-literal-delimiter-face))))
 '(nxml-name-face ((t (:inherit nxml-element-local-name-face))))
 '(nxml-namespace-attribute-colon-face ((t (:inherit nxml-attribute-colon-face))))
 '(nxml-namespace-attribute-prefix-face ((t (:inherit nxml-attribute-local-name-face))))
 '(nxml-namespace-attribute-xmlns-face ((t (:inherit nxml-attribute-local-name-face))))
 '(nxml-processing-instruction-delimiter-face ((t (:inherit nxml-tag-delimiter-face))))
 '(nxml-prolog-keyword-face ((t (:inherit nxml-prolog-literal-delimiter-face))))
 '(nxml-prolog-literal-content-face ((t (:inherit nxml-prolog-literal-delimiter-face))))
 '(nxml-prolog-literal-delimiter-face ((t (:foreground "white"))))
 '(nxml-ref-face ((t (:foreground "white"))))
 '(nxml-tag-delimiter-face ((t (:foreground "SlateGrey"))))
 '(nxml-tag-slash-face ((t (:inherit nxml-tag-delimiter-face))))
 '(nxml-text-face ((t (:foreground "#cccccc")))))


;; useful for term mode though ...

;;  '(nxml-attribute-colon-face ((t (:inherit nxml-attribute-local-name-face :foreground "yellow"))))
;;  '(nxml-attribute-local-name-face ((t (:background "black" :foreground "cyan"))))
;;  '(nxml-attribute-prefix-face ((t (:inherit nxml-attribute-local-name-face))))
;;  '(nxml-attribute-value-delimiter-face ((t (:inherit nxml-attribute-value-face))))
;;  '(nxml-attribute-value-face ((t (:background "black" :foreground "white"))))
;;  '(nxml-comment-content-face ((t (:foreground "FireBrick" :weight bold))))
;;  '(nxml-comment-delimiter-face ((t (:inherit nxml-comment-content-face))))
;;  '(nxml-delimited-data-face ((((class color) (background light)) (:inherit nxml-name-face))))
;;  '(nxml-delimiter-face ((t (:inherit nxml-name-face))))
;;  '(nxml-element-colon-face ((t (:inherit nxml-element-local-name-face :foreground "black" :weight bold))))
;;  '(nxml-element-local-name-face ((t (:background "black" :foreground "blue" :weight bold))))
;;  '(nxml-element-prefix-face ((t (:inherit nxml-element-local-name-face))))
;;  '(nxml-entity-ref-name-face ((t (:inherit nxml-ref-face))))
;;  '(nxml-markup-declaration-delimiter-face ((t (:inherit nxml-prolog-literal-delimiter-face))))
;;  '(nxml-name-face ((((class color) (background light)) (:background "black" :foreground "white"))))
;;  '(nxml-namespace-attribute-colon-face ((t (:inherit nxml-attribute-colon-face))))
;;  '(nxml-namespace-attribute-prefix-face ((t (:inherit nxml-attribute-local-name-face))))
;;  '(nxml-namespace-attribute-xmlns-face ((t (:inherit nxml-attribute-local-name-face))))
;;  '(nxml-processing-instruction-delimiter-face ((t (:inherit nxml-delimiter-face))))
;;  '(nxml-prolog-keyword-face ((t (:inherit nxml-prolog-literal-delimiter-face))))
;;  '(nxml-prolog-literal-content-face ((t (:inherit nxml-prolog-literal-delimiter-face))))
;;  '(nxml-prolog-literal-delimiter-face ((t (:foreground "black" :weight bold))))
;;  '(nxml-ref-face ((((class color) (background light)) (:foreground "white"))))
;;  '(nxml-tag-delimiter-face ((t (:inherit nxml-tag-slash-face))))
;;  '(nxml-tag-slash-face ((t (:inherit nxml-element-prefix-face))))
;;  '(nxml-text-face ((t (:foreground "white" :weight bold))))
;;  '(rng-error-face ((t (:background "red" :foreground "white")))))


;; -------------------------------------------------------------------------

(defun my-color-theme ()
  "Color theme by tav, created 2004-11-19."
  (interactive)
  (color-theme-install
   '(my-color-theme
     ((background-color . "black")
      (background-mode . dark)
      (border-color . "black")
      (cursor-color . "yellow")
      (foreground-color . "white")
      (foreground-color . "#cccccc")
      (mouse-color . "sienna1"))
     ((display-time-mail-face . mode-line)
      (help-highlight-face . underline)
      (list-matching-lines-face . bold)
; ori:
;      (rst-block-face . font-lock-keyword-face)
      (rst-block-face . font-lock-comment-face)
      (rst-comment-face . font-lock-comment-face)
      (rst-definition-face . font-lock-function-name-face)
      (rst-directive-face . font-lock-builtin-face)
      (rst-emphasis1-face quote italic)
      (rst-emphasis2-face quote bold)
      (rst-external-face . font-lock-type-face)
      (rst-literal-face . font-lock-string-face)
      (rst-reference-face . font-lock-variable-name-face)
      (widget-mouse-face . highlight))
     (default ((t (:stipple nil :background "black" :foreground "White" :inverse-video nil :box nil :strike-through nil :overline nil :underline nil :slant normal :weight normal :height 116 :width normal :family "adobe-courier"))))
     (Doc ((t (:foreground "Red"))))
     (Stop ((t (:background "Red" :foreground "White"))))
     (blue ((t (:foreground "blue"))))
     (bold ((t (:bold t :weight bold))))
     (bold-italic ((t (:bold t :weight bold))))
     (border ((t (:background "black"))))
     (border-glyph ((t (nil))))
     (buffers-tab ((t (:background "black" :foreground "white"))))
     (calendar-today-face ((t (:underline t))))
     (comint-highlight-input ((t (:bold t :weight bold))))
     (comint-highlight-prompt ((t (:foreground "cyan"))))
     (cperl-array-face ((t (:foreground "darkseagreen"))))
     (cperl-hash-face ((t (:foreground "darkseagreen"))))
     (cperl-nonoverridable-face ((t (:foreground "SkyBlue"))))
     (cursor ((t (:background "yellow"))))
     (custom-button-face ((t (nil))))
     (custom-changed-face ((t (:background "blue" :foreground "white"))))
     (custom-documentation-face ((t (nil))))
     (custom-face-tag-face ((t (:underline t))))
     (custom-group-tag-face ((t (:foreground "light blue" :underline t))))
     (custom-group-tag-face-1 ((t (:foreground "pink" :underline t))))
     (custom-invalid-face ((t (:background "red" :foreground "yellow"))))
     (custom-modified-face ((t (:background "blue" :foreground "white"))))
     (custom-rogue-face ((t (:background "black" :foreground "pink"))))
     (custom-saved-face ((t (:underline t))))
     (custom-set-face ((t (:background "white" :foreground "blue"))))
     (custom-state-face ((t (:foreground "lime green"))))
     (custom-variable-button-face ((t (:bold t :underline t :weight bold))))
     (custom-variable-tag-face ((t (:foreground "light blue" :underline t))))
     (diary-face ((t (:foreground "IndianRed"))))
     (erc-action-face ((t (:bold t :weight bold))))
     (erc-bold-face ((t (:bold t :weight bold))))
     (erc-default-face ((t (nil))))
     (erc-direct-msg-face ((t (:foreground "sandybrown"))))
     (erc-error-face ((t (:bold t :foreground "IndianRed" :weight bold))))
     (erc-input-face ((t (:foreground "Beige"))))
     (erc-inverse-face ((t (:background "wheat" :foreground "darkslategrey"))))
     (erc-notice-face ((t (:foreground "MediumAquamarine"))))
     (erc-pal-face ((t (:foreground "pale green"))))
     (erc-prompt-face ((t (:foreground "MediumAquamarine"))))
     (erc-underline-face ((t (:underline t))))
     (eshell-ls-archive-face ((t (:bold t :foreground "IndianRed" :weight bold))))
     (eshell-ls-backup-face ((t (:foreground "Grey"))))
     (eshell-ls-clutter-face ((t (:foreground "DimGray"))))
     (eshell-ls-directory-face ((t (:bold t :foreground "MediumSlateBlue" :weight bold))))
     (eshell-ls-executable-face ((t (:foreground "Coral"))))
     (eshell-ls-missing-face ((t (:foreground "black"))))
     (eshell-ls-picture-face ((t (:foreground "Violet"))))
     (eshell-ls-product-face ((t (:foreground "sandybrown"))))
     (eshell-ls-readonly-face ((t (:foreground "Aquamarine"))))
     (eshell-ls-special-face ((t (:foreground "Gold"))))
     (eshell-ls-symlink-face ((t (:foreground "White"))))
     (eshell-ls-unreadable-face ((t (:foreground "DimGray"))))
     (eshell-prompt-face ((t (:foreground "MediumAquamarine"))))
     (fixed-pitch ((t (:family "courier"))))
     (fl-comment-face ((t (:foreground "pink"))))
     (fl-doc-string-face ((t (:foreground "purple"))))
     (fl-function-name-face ((t (:foreground "red"))))
     (fl-keyword-face ((t (:foreground "cadetblue"))))
     (fl-string-face ((t (:foreground "green"))))
     (fl-type-face ((t (:foreground "yellow"))))
     (font-lock-builtin-face ((t (:foreground "LightSteelBlue"))))
;     (font-lock-comment-face ((t (:foreground "SlateGrey"))))
; ori:
     (font-lock-comment-face ((t (:foreground "IndianRed"))))
;     (font-lock-comment-face ((t (:foreground "Sienna2"))))
     (font-lock-constant-face ((t (:foreground "Aquamarine"))))
     (font-lock-doc-face ((t (:foreground "grey"))))
;     (font-lock-doc-face ((t (:bold t :foreground "white" :weight bold))))
; ori:
     (font-lock-doc-string-face ((t (:foreground "DarkOrange"))))
;     (font-lock-doc-string-face ((t (:foreground "pale green"))))
     (font-lock-function-name-face ((t (:foreground "YellowGreen"))))
     (font-lock-keyword-face ((t (:foreground "Aquamarine"))))
     (font-lock-preprocessor-face ((t (:foreground "Aquamarine"))))
     (font-lock-reference-face ((t (:foreground "SlateBlue"))))
; ori:
     (font-lock-string-face ((t (:foreground "Orange"))))
;     (font-lock-string-face ((t (:foreground "pale green"))))
     (font-lock-type-face ((t (:foreground "SlateGrey"))))
     (font-lock-variable-name-face ((t (:foreground "darkseagreen"))))
     (font-lock-warning-face ((t (:bold t :foreground "Pink" :weight bold))))
     (fringe ((t (:background "grey10"))))
     (gnus-cite-attribution-face ((t (nil))))
     (gnus-cite-face-1 ((t (:bold t :foreground "deep sky blue" :weight bold))))
     (gnus-cite-face-10 ((t (:foreground "medium purple"))))
     (gnus-cite-face-11 ((t (:foreground "turquoise"))))
     (gnus-cite-face-2 ((t (:bold t :foreground "cadetblue" :weight bold))))
     (gnus-cite-face-3 ((t (:bold t :foreground "gold" :weight bold))))
     (gnus-cite-face-4 ((t (:foreground "light pink"))))
     (gnus-cite-face-5 ((t (:foreground "pale green"))))
     (gnus-cite-face-6 ((t (:bold t :foreground "chocolate" :weight bold))))
     (gnus-cite-face-7 ((t (:foreground "orange"))))
     (gnus-cite-face-8 ((t (:foreground "magenta"))))
     (gnus-cite-face-9 ((t (:foreground "violet"))))
     (gnus-emphasis-bold ((t (:bold t :weight bold))))
     (gnus-emphasis-bold-italic ((t (:bold t :weight bold))))
     (gnus-emphasis-highlight-words ((t (:background "black" :foreground "yellow"))))
     (gnus-emphasis-italic ((t (nil))))
     (gnus-emphasis-underline ((t (:underline t))))
     (gnus-emphasis-underline-bold ((t (:bold t :underline t :weight bold))))
     (gnus-emphasis-underline-bold-italic ((t (:bold t :underline t :weight bold))))
     (gnus-emphasis-underline-italic ((t (:underline t))))
     (gnus-group-mail-1-empty-face ((t (:foreground "aquamarine1"))))
     (gnus-group-mail-1-face ((t (:bold t :foreground "aquamarine1" :weight bold))))
     (gnus-group-mail-2-empty-face ((t (:foreground "aquamarine2"))))
     (gnus-group-mail-2-face ((t (:bold t :foreground "aquamarine2" :weight bold))))
     (gnus-group-mail-3-empty-face ((t (:foreground "aquamarine3"))))
     (gnus-group-mail-3-face ((t (:bold t :foreground "aquamarine3" :weight bold))))
     (gnus-group-mail-low-empty-face ((t (:foreground "aquamarine4"))))
     (gnus-group-mail-low-face ((t (:bold t :foreground "aquamarine4" :weight bold))))
     (gnus-group-news-1-empty-face ((t (:foreground "PaleTurquoise"))))
     (gnus-group-news-1-face ((t (:bold t :foreground "PaleTurquoise" :weight bold))))
     (gnus-group-news-2-empty-face ((t (:foreground "turquoise"))))
     (gnus-group-news-2-face ((t (:bold t :foreground "turquoise" :weight bold))))
     (gnus-group-news-3-empty-face ((t (nil))))
     (gnus-group-news-3-face ((t (:bold t :weight bold))))
     (gnus-group-news-4-empty-face ((t (nil))))
     (gnus-group-news-4-face ((t (:bold t :weight bold))))
     (gnus-group-news-5-empty-face ((t (nil))))
     (gnus-group-news-5-face ((t (:bold t :weight bold))))
     (gnus-group-news-6-empty-face ((t (nil))))
     (gnus-group-news-6-face ((t (:bold t :weight bold))))
     (gnus-group-news-low-empty-face ((t (:foreground "DarkTurquoise"))))
     (gnus-group-news-low-face ((t (:bold t :foreground "DarkTurquoise" :weight bold))))
     (gnus-header-content-face ((t (:foreground "forest green"))))
     (gnus-header-from-face ((t (:bold t :foreground "spring green" :weight bold))))
     (gnus-header-name-face ((t (:foreground "deep sky blue"))))
     (gnus-header-newsgroups-face ((t (:bold t :foreground "purple" :weight bold))))
     (gnus-header-subject-face ((t (:bold t :foreground "orange" :weight bold))))
     (gnus-signature-face ((t (:bold t :foreground "khaki" :weight bold))))
     (gnus-splash-face ((t (:foreground "Brown"))))
     (gnus-summary-cancelled-face ((t (:background "black" :foreground "yellow"))))
     (gnus-summary-high-ancient-face ((t (:bold t :foreground "SkyBlue" :weight bold))))
     (gnus-summary-high-read-face ((t (:bold t :foreground "PaleGreen" :weight bold))))
     (gnus-summary-high-ticked-face ((t (:bold t :foreground "pink" :weight bold))))
     (gnus-summary-high-unread-face ((t (:bold t :weight bold))))
     (gnus-summary-low-ancient-face ((t (:foreground "SkyBlue"))))
     (gnus-summary-low-read-face ((t (:foreground "PaleGreen"))))
     (gnus-summary-low-ticked-face ((t (:foreground "pink"))))
     (gnus-summary-low-unread-face ((t (nil))))
     (gnus-summary-normal-ancient-face ((t (:foreground "SkyBlue"))))
     (gnus-summary-normal-read-face ((t (:foreground "PaleGreen"))))
     (gnus-summary-normal-ticked-face ((t (:foreground "pink"))))
     (gnus-summary-normal-unread-face ((t (nil))))
     (gnus-summary-selected-face ((t (:underline t))))
     (green ((t (:foreground "green"))))
     (gui-button-face ((t (:background "grey75" :foreground "black"))))
     (gui-element ((t (:background "#D4D0C8" :foreground "black"))))
     (header-line ((t (:box (:line-width 1 :style released-button) :background "grey20" :foreground "grey90" :box nil))))
     (highlight ((t (:background "darkolivegreen"))))
     (highline-face ((t (:background "SeaGreen"))))
     (holiday-face ((t (:background "DimGray"))))
     (info-menu-5 ((t (:underline t))))
     (info-node ((t (:bold t :foreground "DodgerBlue1" :underline t :weight bold))))
     (info-xref ((t (:foreground "DodgerBlue1" :underline t))))
     (isearch ((t (:background "blue"))))
     (isearch-lazy-highlight-face ((t (:background "paleturquoise4"))))
     (isearch-secondary ((t (:foreground "red3"))))
     (italic ((t (nil))))
     (left-margin ((t (nil))))
     (list-mode-item-selected ((t (:background "gray68" :foreground "white"))))
     (menu ((t (nil))))
     (message-cited-text-face ((t (:bold t :foreground "green" :weight bold))))
     (message-header-cc-face ((t (:bold t :foreground "green4" :weight bold))))
     (message-header-name-face ((t (:bold t :foreground "orange" :weight bold))))
     (message-header-newsgroups-face ((t (:bold t :foreground "violet" :weight bold))))
     (message-header-other-face ((t (:bold t :foreground "chocolate" :weight bold))))
     (message-header-subject-face ((t (:bold t :foreground "yellow" :weight bold))))
     (message-header-to-face ((t (:bold t :foreground "cadetblue" :weight bold))))
     (message-header-xheader-face ((t (:bold t :foreground "light blue" :weight bold))))
     (message-mml-face ((t (:bold t :foreground "Green3" :weight bold))))
     (message-separator-face ((t (:foreground "blue3"))))
     (mode-line ((t (:background "DarkRed" :foreground "white" :box (:line-width 1 :style released-button)))))
     (modeline-buffer-id ((t (:background "DarkRed" :foreground "white"))))
     (modeline-mousable ((t (:background "DarkRed" :foreground "white"))))
     (modeline-mousable-minor-mode ((t (:background "DarkRed" :foreground "white"))))
     (mouse ((t (:background "sienna1"))))
     (p4-depot-added-face ((t (:foreground "blue"))))
     (p4-depot-deleted-face ((t (:foreground "red"))))
     (p4-depot-unmapped-face ((t (:foreground "grey30"))))
     (p4-diff-change-face ((t (:foreground "dark green"))))
     (p4-diff-del-face ((t (:foreground "red"))))
     (p4-diff-file-face ((t (:background "gray90"))))
     (p4-diff-head-face ((t (:background "gray95"))))
     (p4-diff-ins-face ((t (:foreground "blue"))))
     (pointer ((t (nil))))
     (primary-selection ((t (:background "blue"))))
     (qt-classes-face ((t (:foreground "Red"))))
     (red ((t (:foreground "red"))))
     (region ((t (:background "blue"))))
     (right-margin ((t (nil))))
     (rst-level-1-face ((t nil)))
     (rst-level-2-face ((t nil)))
     (rst-level-3-face ((t nil)))
     (rst-level-4-face ((t nil)))
     (rst-level-5-face ((t nil)))
     (rst-level-6-face ((t nil)))
     (scroll-bar ((t (:background "grey75"))))
     (secondary-selection ((t (:background "darkslateblue"))))
     (show-paren-match-face ((t (:background "Aquamarine" :foreground "SlateBlue"))))
     (show-paren-mismatch-face ((t (:background "Red" :foreground "White"))))
     (text-cursor ((t (:background "yellow" :foreground "black"))))
     (tool-bar ((t (nil))))
     (tooltip ((t (:background "lightyellow" :foreground "black"))))
     (trailing-whitespace ((t (:background "red"))))
     (underline ((t (:underline nil))))
     (variable-pitch ((t (:family "helv"))))
     (vertical-divider ((t (nil))))
     (widget ((t (nil))))
     (widget-button-face ((t (:bold t :weight bold))))
     (widget-button-pressed-face ((t (:foreground "red"))))
     (widget-documentation-face ((t (:foreground "lime green"))))
     (widget-field-face ((t (:background "dim gray"))))
     (widget-inactive-face ((t (:foreground "light gray"))))
     (widget-single-line-field-face ((t (:background "dim gray"))))
     (woman-bold-face ((t (:bold t :weight bold))))
     (woman-italic-face ((t (:foreground "beige"))))
     (woman-unknown-face ((t (:foreground "LightSalmon"))))
     (yellow ((t (:foreground "yellow"))))
     (zmacs-region ((t (:background "snow" :foreground "blue")))))))

;
; support for restructured text editing
;

(defun replace-lines (fromchar tochar)
  ;; by David Goodger
  "Replace flush-left lines, consisting of multiple FROMCHAR characters, with
equal-length lines of TOCHAR."
  (interactive "\
cSearch for flush-left lines of char:
cand replace with char: ")
  (save-excursion
    (let* ((fromstr (string fromchar))
	   (searchre (concat "^" (regexp-quote fromstr) "+ *$"))
	   (found 0))
      (condition-case err
	  (while t
	    (search-forward-regexp searchre)
	    (setq found (1+ found))
	    (search-backward fromstr)  ;; point will be *before* last char
	    (setq p (1+ (point)))
	    (beginning-of-line)
	    (setq l (- p (point)))
	    (kill-line)
	    (insert-char tochar l))
	(search-failed
	 (message (format "%d lines replaced." found)))))))

(defun repeat-last-character ()
  ;; by Martin Blais
  "Fills the current line up to the length of the preceding line (if not empty),
using the last character on the current line. If the preceding line is empty, or
if a prefix argument is provided, fill up to the fill-column.

If the current line is longer than the desired length, shave the characters off
the current line to fit the desired length.

As an added convenience, if the command is repeated immediately, the alternative
behaviour is performed."

;; TODO
;; ----
;; It would be useful if only these characters were repeated:
;; =-`:.'"~^_*+#<>!$%&(),/;?@[\]{|}
;; Especially, empty lines shouldn't be repeated.

  (interactive)
  (let* ((curcol (current-column))
	 (curline (+ (count-lines (point-min) (point)) (if (eq curcol 0) 1 0)))
	 (lbp (line-beginning-position 0))
	 (prevcol (if (= curline 1)
		      fill-column
		    (save-excursion
		      (forward-line -1)
		      (end-of-line)
		      (skip-chars-backward " \t" lbp)
		      (let ((cc (current-column)))
			(if (= cc 0) fill-column cc)))))
	 (rightmost-column
	  (cond (current-prefix-arg fill-column)
		((equal last-command 'repeat-last-character)
		 (if (= curcol fill-column) prevcol fill-column))
		(t (save-excursion
		     (if (= prevcol 0) fill-column prevcol))) )) )
    (end-of-line)
    (if (> (current-column) rightmost-column)
	;; shave characters off the end
	(delete-region (- (point)
			  (- (current-column) rightmost-column))
		       (point))
      ;; fill with last characters
      (insert-char (preceding-char)
		   (- rightmost-column (current-column)))) ))

(defun reST-title-char-p (c)
  ;; by Martin Blais
  "Returns true if the given character is a valid title char."
  (and (string-match "[-=`:\\.'\"~^_*+#<>!$%&(),/;?@\\\|]" 
		     (char-to-string c)) t))

(defun reST-forward-title ()
  ;; by Martin Blais
  "Skip to the next restructured text section title."
  (interactive)
  (let* ( (newpoint
	   (save-excursion
	     (forward-char) ;; in case we're right on a title
	     (while
	       (not
		(and (re-search-forward "^[A-Za-z0-9].*[ \t]*$" nil t)
		     (reST-title-char-p (char-after (+ (point) 1)))
		     (looking-at (format "\n%c\\{%d,\\}[ \t]*$" 
					 (char-after (+ (point) 1)) 
					 (current-column))))))
	     (beginning-of-line)
	     (point))) )
    (if newpoint (goto-char newpoint)) ))

(defun reST-backward-title ()
  ;; by Martin Blais
  "Skip to the previous restructured text section title."
  (interactive)
  (let* ( (newpoint
	   (save-excursion
	     ;;(forward-char) ;; in case we're right on a title
	     (while
	       (not
		(and (or (backward-char) t)
		     (re-search-backward "^[A-Za-z0-9].*[ \t]*$" nil t)
		     (or (end-of-line) t)
		     (reST-title-char-p (char-after (+ (point) 1)))
		     (looking-at (format "\n%c\\{%d,\\}[ \t]*$" 
					 (char-after (+ (point) 1)) 
					 (current-column))))))
	     (beginning-of-line)
	     (point))) )
    (if newpoint (goto-char newpoint)) ))

(defun join-paragraph ()
  ;; by David Goodger
  "Join lines in current paragraph into one line, removing end-of-lines."
  (interactive)
  (save-excursion
    (backward-paragraph 1)
    (forward-char 1)
    (let ((start (point)))	; remember where we are
      (forward-paragraph 1)	; go to the end of the paragraph
      (beginning-of-line 0)	; go to the beginning of the previous line
      (while (< start (point))	; as long as we haven't passed where we started
	(delete-indentation)	; join this line to the line before
	(beginning-of-line)))))	; and go back to the beginning of the line

(defun force-fill-paragraph ()
  ;; by David Goodger
  "Fill paragraph at point, first joining the paragraph's lines into one.
This is useful for filling list item paragraphs."
  (interactive)
  (join-paragraph)
  (fill-paragraph nil))

(global-set-key [?\C-c ?a] 'repeat-last-character)
(global-set-key [?\C-c ?\C-p] 'reST-backward-title)
(global-set-key [?\C-c ?\C-n] 'reST-forward-title)
(global-set-key [?\C-c ?\C-l] 'rst-adjust)
(global-set-key [?\C-c ?\C-t] 'rst-toc)
(global-set-key [?\C-c ?\C-r] 'rst-display-decorations-hierarchy)

(setq rst-preferred-decorations '( (?= over-and-under 0)
								   (?- over-and-under 0)
								   (?= simple 0)
								   (?- simple 0)
								   (?~ simple 0)
								   (?+ simple 0)
								   (?` simple 0)
								   (?# simple 0)
								   (?@ simple 0) ))

; do C-c C-h to see a list of keybindings starting with C-c

; other functions:

; rst-backward-section
; rst-forward-section
; rst-shift-region-right
; rst-shift-region-left
; rst-enumerate-region
; rst-listify-region
; rst-straighten-bullets-region
; rst-toggle-line-block

; enable rst "lists" to be recognised as paragraph boundaries

(add-hook 'text-mode-hook 'rst-set-paragraph-separation)

;
; load up certain things depending on whether we are in a windowed system or not
;

(defun set-my-preferences () "set up things the way i like"
  (my-color-theme)
  (server-start)
  ; (set-face-font 'menu "6x10")
  (set-face-foreground 'menu "white")
  (set-face-background 'menu "black")
  ; (set-default-font "-misc-fixed-medium-r-semicondensed--13-120-75-75-c-60-iso8859-1")
  (set-border-color "SlateGray"))

(if window-system
    (set-my-preferences))

;
; limit the width to the holy 80 for use in auto-fill-mode
;

;; used by tab-to-tab-stop
;; default in indent.el: '(8 16 24 32 40 48 56 64 72 80 88 96 104 112 120)

(setq tab-stop-list 
	  '(4 8 12 16 20 24 28 32 36 40 44 48 52 56 60 64
		  68 72 76 80 84 88 92 96 100 104 108 112 116 120))

(defun set-my-fill-column() "set the fill column width" (interactive)
  (setq default-tab-width 4)
  (set-fill-column 80)
  (setq indent-tabs-mode nil))

(add-hook 'after-init-hook 'set-my-fill-column)

(defun my-rst-mode-hook()
  "dealing with text mode which seems to fuck with things"
  (interactive)
  (set-my-fill-column))

(add-hook 'rst-mode-hook 'my-rst-mode-hook)

(defun my-python-mode-hook()
  "dealing with text mode which seems to fuck with things"
  (interactive)
  (setq indent-tabs-mode nil)
  (global-set-key [backspace] 'py-electric-backspace)
  (setq default-fill-column 80)
  )

(add-hook 'python-mode-hook 'my-python-mode-hook)

(defun my-javascript-mode-hook()
  "dealing with text mode which seems to fuck with things"
  (interactive)
  (setq indent-tabs-mode nil)
  (setq default-tab-width 4)
  (setq default-fill-column 80)
  )

(add-hook 'javascript-mode-hook 'my-javascript-mode-hook)

(setq default-fill-column 80)
(setq indent-tabs-mode nil)

(global-set-key "\C-q" 'fill-paragraph)

(setq sentence-end-double-space nil)
;; (setq sentence-end ...)

;
; count the lines
;

(defun count-words () "count the number of characters/words/lines in the buffer"
  (interactive)
  (save-excursion
    (let ((opoint (point)) beg end total before after)
      (forward-page)
      (beginning-of-line)
      (or (looking-at page-delimiter) (end-of-line))
      (setq end (point))
      (backward-page)
      (setq beg (point))
      (setq total (count-lines beg end)
	    before (count-lines beg opoint)
	    after (count-lines opoint end))
      (message "buffer has %d lines (%d + %d)" total before after))))

(defun select-buffer () "select all powah... like ^a in windows"
  (interactive)
  (push-mark (point))
  (push-mark (point-max) nil t)
  (goto-char (point-min)))

(global-set-key [?\C-c ?w] 'count-words)
(global-set-key [?\C-c ?b] 'select-buffer)

;
; load up personal .emacs settings
;

;; (setq my-private-customisations "~/.emacs.personal")
;; (load my-private-customisations)

;
; save place in buffer for future sessions
;

(setq-default save-place t)
(setq save-place-file "~/.emacs.places")
(setq save-place-version-control "nospecial")

;
; session (also checkout recentf)
;

;; (require 'recentf)
;; (recentf-mode 1)

; (add-to-list 'load-path "/home/tav/.site-lisp/session")

; (setq session-save-file "~/.emacs.sessions")

; (require 'session)
; (add-hook 'after-init-hook 'session-initialize)

;
; desktop power!
;

(require 'desktop)
(setq desktop-globals-to-save '(desktop-missing-file-warning))

(desktop-load-default)
(desktop-read)

;
; set a menu
;

(define-key global-map [menu-bar extra] 
  (cons "E" (make-sparse-keymap "E")))

(global-set-key [menu-bar extra emacs] '(".emacs" . dot-emacs ))

;; (session-add-submenu '("Open...recently visiteda"
;;					   :included file-name-history
;;					   :filter session-file-opened-menu-filter))

;
; keyboard macros rock!
;

;; to start: C-x (
;; to end: C-x )

;; functions:
;;   apply-macro-to-region-lines
;;   name-last-kbd-macro
;;   insert-kbd-macro

(fset 'left-indent-4
   "\C-a\C-d\C-d\C-d\C-d")


; (add-to-list 'load-path "/home/tav/.site-lisp/graphviz-dot-mode")
; (load-file "/home/tav/.site-lisp/graphviz-dot-mode/graphviz-dot-mode.el")

;;(defun look-here
;  (

(defcustom espian-nick nil
  "The espian nick for usage in comment logs, jumps, etc."
  :type 'string
  :group 'change-log)

;; C-C make and open in web browser

;(setq this-frame (selected-frame))
;(make-variable-frame-local 'espian-nick)

;
; timestamping support
;

;; (add-hook 'write-file-hooks 'time-stamp)

;; (setq time-stamp-start "Time-stamp:[ 	]+\\\\?[\"<]+")
;; (setq time-stamp-end "\\\\?[\">]")
;; (setq time-stamp-format "%:y-%02m-%02d %02H:%02M:%02S %u")
;; (setq time-stamp-start "last-modified [\[]")
;; (setq time-stamp-end "[\]]")
;; (setq time-stamp-start ":X-Updated:[ \t]+\\\\?[\"<]+")
;; (setq time-stamp-end "\\\\?[\">]")

(setq time-stamp-start ":X-Updated: [\[]")
(setq time-stamp-end "[\]]")
(setq time-stamp-line-limit 20)
(setq time-stamp-format "%:y-%02m-%02d, %02H:%02M")

; (require 'ebby)

(load-file "/Users/tav/.site-lisp/graphviz-dot-mode.el")