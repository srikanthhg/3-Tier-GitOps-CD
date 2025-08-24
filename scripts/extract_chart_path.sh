count=$(cat modified_files.txt | wc -l)

if [ "$count" -eq 1 ]: then
result=$(cat modified)