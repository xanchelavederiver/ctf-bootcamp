create a first lecture slides - introduction

Audience: Computer science and IT students with basic or programming skills; no CTF experience required and expected
Duration: 90 minutes
Delivery: Mixed lecture, live demonstration, hands-on work
Topics covered:
  - Why CTF, rules, formats, scoring
  - Beyond CTF: other formats (the boxes, red-blue teaming, etc.)
  - Useful References for the beginners:
    i. "where to start" links first - on one slide
    ii. useful resources
        * general info about CS
        * general about CTF - tutorials portals (like PortWagger), endless CTF platforms (e.g. PicoCTF), try hack me and HackTheBox platforms, etc.
        * category-targeted references (useful links to study )
  - the rest is dedicated to a short CTF that is comprised of several tasks that demonstrate the basic CTF categories (see below)
    * the first section must be dedicated to docker - how the server-based tasks are delivered nowadays, how to install docker and start the task, how to cleanup
    * then a dedicated section for each of the tasks
    * the first slide provide info on:
      ** the task's legend
      ** how to access the task (handout file names, connection URL, etc.)
      ** necessary tools - links, installation commands
      ** additional info regarding the task
    * the next slides show the flags to be found and links to the analogous task on PicoCTF (or analogous endless CTF platform)

**IMPORTANT**:

1. the references must include prominent resources in Russian language
2. the references should be beginner-friendly, especially those advised at first


The short CTF:

- the task project folders should reside in `project/tasks/lecture-1/{name-with-category}`
- server tasks must be docker-compose-based projects
- the categories order is `web`, `crypto`, `forensics`, `stego`, `reverse`, `pwn`
- the hole bunch is expected to be solved in one hour, leaving the other 30 minutes for the intro part
- therefore the tasks should be basic, but not completely trivial (like decoding base64 string as a crypto challenge...)
- the tasks should have a hidden depths - some extra flag stores (for web challenge, maybe some other, forensics and stego are an easy ) - to tease the students with `keep looking at home - you might find something else...`

- ideas on the intro challenges:
  * web
    ** the classic flag written directly in the HTML code, but as a base64-encoded string
    ** a custom JS handler fires on some key combination and shows another flag in an alert or a pop-up window
    ** smth that would require creating an HTTP request using `curl`
    ** basic, easy to trigger template injection
    ** smth. else?
    ** no fancy web technologies, just plain HTML, JS, and CSS; a server is python-based (so the template injection is python-based as well)
  * crypto
    ** Caesar, ROT13
    ** XOR oracle:
       *** a server with the unknown key file encrypts everything we send it
       *** the flag is given in the encrypted form - using this unknown key
       *** the server refuses to decrypt the encrypted flag (it verifies if the encryption result equals the flag - it is also a hint for the students)
       *** can be a web-based so it is solvable using curl and base64 util
    ** a python script that uses AES to encrypt file:
       *** the key is derived based on time in seconds
       *** the file is encrypted and saved as file
       *** its creation time gives away the approximate time of encryption
  * forensics
    ** a .pcapng with file traffic capture over insecure FTP server - so it is possible to get the password and connect to this FTP server directly and grab the files; otherwise just fetch the files with TCP flow (show the both ways)
    ** the file is a password-protected archive, flag in its metadata
    ** password-cracking gives another flag
    ** smth. else?
  * stego
    ** LSB in a PNG image (to solve it using `stegsolve` - or is there a better suited tool?..)
    ** smth. else?
  * reverse
    ** a trivial util that checks several flags:
       *** one flag is checked by simple `strcmp` - so `strings` can be used to "solve" the task
       *** another flag is stored encrypted - XORed with some key and is decrypted in a constructor when the binary starts - so debugging would reveal the flag
       *** the third flag 
       *** these flags are verified by separate checks, if any of these three flags are entered the util shows `Access granted`, otherwise `Access denied`
  * pwn
    ** the simplest bof that can be used to steer execution to the function that prints the flag
    ** socat-based util


Create writeups - for the lecturer and later to be given to the students.

N.B. these tasks are for beginners!


The export should prepare the lecture slides in PDF format with `tasks` folder that contains the tasks to be run on their machines (for homework)


make an implementation plan, save at `.claude/plans/01-{name}.md`
