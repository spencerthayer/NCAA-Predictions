
all: ./data/elo.csv
	head ./data/elo.csv

./data/all_data.csv: ./data/RegularSeasonDetailedResults.csv ./data/TourneyDetailedResults.csv
	python -c "from ncaapredictions.io import read_all_data; read_all_data('./data').to_csv('./data/all_data.csv', index=False)"	

./data/elo.csv: ./data/all_data.csv
	python -c "from ncaapredictions.ncaa import build_elo_data; build_elo_data()"

clean:
	rm ./data/all_data.csv
	rm ./data/elo.csv

