# dirDetector
a simple crawler with multithreading to detect sensitive diretories.
Explain: It's as a plugin, so the interface can be a little strange.

# usage
python DirDetector url [ threadAmount ]

# about sensitiveWords.txt
This file includes all custom sensitive words and corresponding description, which will be used to whether a link is sensitive.
Note: the format is like:
sensitiveWord --> description about it
