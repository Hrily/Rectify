# oldcwd=$(pwd)
# cd $1
python add_problem.py $1 $2

if [ $? -eq 69 ]
then
echo "bye"
exit
fi

for file in $(find $1 -name *.db_insert)
do
    echo "executing mongo " $db " < " $file
    mongo RectifyTest < $file
done