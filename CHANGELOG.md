# CHANGELOG

* _main() as an entry point:_ Most of the execution logic/sequencing is currently done outside of a function. You properly handle the condition in which the script is run from the command line by checking the invocation context (if __name__ == '__main__': ), but I've moved much of that sequencing to a discrete function (main()) which you then call from your conditional as it exists today. This allows you to consider using your application as a module and importing it from another script/application with only a few minor changes. But more importantly I've found it forces me to be sure my logic is sound and linear and allows for a third-party to more easily follow the story line of what I'm trying to do.
* _argparse instead of argv_: I moved your argument handling to the argparse library and you can see it fits naturally as the start of the program at our new entry point.  It should be self-explanatory if you run _python summarize.py -h_ but I wanted to be extra mindful to not change the functionality or your intentional choices for handling user input. You'll note this is the start of my mission against making calls directly to the OS and allowing libraries to do that work for us. :)
  * _-b (basename):_ I wasn't sure if you wanted to give the user the opportunity to set a base_name as an alternative to inferring it from the URL/filename.  So there's an optional parameter that will set the base_name to user input.  NB: I got lazy and passed the variable around a bit to avoid having to make two calls to helper functions - I guess the right way to do it would be to create an object of type Document and read its state and ignore its base_name if we set it manually, but alas, this is good enough for government work 
  
  * _mutual exclusion:_ It'd not be difficult to fire off a list of articles/documents you wanted to summarize but again, since I didn't want to change the original functionality, I allowed the user to specify -f or -u, but not both
* _requests vs. curl_:  I had a debate with myself as to whether or not to use the requests library
    or the system-call to curl as you've done below.  i ended up siding with requests because:
  * some OS-level issue with curl e.g. nonstandard implementation, not in path, etc. and 
  * requests gives us some clue into the type of document returned rather than having to rely on filename
* _Pathlib vs. os.path: For similar reasons to what I mentioned earlier, I like using Pathlib to handle navigating directory structures and so I used a pretty trivial example in your code. It's more powerful than I demonstrate in that you can test permissions, etc. before writing.  In your case I changed the destination of the downloaded file to the user's home directory since they may not have access to the rootlevel /tmp but feel free to change to whatever you'd like obviously.

_Miscellany_

* I used a bit of lazy hackery to get around a condition I found in which a URL ended with a trailing slash, nothing after it, yet supplied a PDF file.  I opted to rely more on the guesswork from libmagic and PDFReader vs. trying to intuit the type of file from the filename itself
* I tried to take about 300 lines of code in the latter half of your original execution logic and put them into separate functions as best I could ,but I did **not** continue adjusting the design pattern/syntax and rather just copied and pasted.
* I've mentioned this a bunch of times now but as I got near the end I couldn't help but hate the fact that I don't have more time because I ended up passing variables around like crazy whereas constructing an object of type Article or something where we can access its state from anywhere.  For another day :)

# BROKEN
I left the attribution portion broken because I lost track of the original URL variable :)  It's commented out.


