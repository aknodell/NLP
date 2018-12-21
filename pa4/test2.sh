for file in ~/CSCE689/finalProject/data/tokens/neg/*
do
	./tagchunk.i686 -predict . w-5-lc "$file" resources > ~/CSCE689/finalProject/data/taggedTokens/neg/${file##*/}.out
done
