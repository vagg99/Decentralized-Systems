# Ελεγχος version pyspark .. Θέλουμε το 3.4.1
import pyspark
print(pyspark.__version__)

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, monotonically_increasing_id
from pyspark.sql.types import FloatType
import pandas as pd

# Διαβάζομε τα δεδομένα

tour_occ_ninat = "data/tour_occ_ninat.xlsx"


excel_data = pd.read_excel(tour_occ_ninat, header=8)

# Κάνω το excel σε csv για να το βαλω στην spark , επειδη δεν μου δουλευε το spark-excel

excel_data.to_csv("data/excel_data.csv", index=False)

# Φτιάχνουμε ενα spark session
spark = SparkSession.builder.appName("EurostatAnalysis").getOrCreate()
# Διαβαζουμε το csv με την spark

spark_df = spark.read.option("header", "true").csv("data/excel_data.csv")
# Ενα print για να δουμε οτι διαβασαμε σωστα τα δεδομενα
spark_df.show(spark_df.count(), truncate=False)
# Αντικαθηστώ το ":" με 0 για να βγουν σωστά οι μέσοι όροι
# και οποιοδήποτε αλλο string γινεται 0

year_columns = [col for col in spark_df.columns if col.startswith("20")]
for year_col in year_columns:
    spark_df = spark_df.withColumn(
        year_col,
        when(col(year_col).cast(FloatType()).isNotNull(), col(year_col).cast(FloatType())).otherwise(0.0)
    )


    # Βλέπω ότι οπου ειχε string τώρα εχει 0
# Αρίθμηση χωρών απο
spark_df = spark_df.withColumn("id", monotonically_increasing_id() + 1)
cols = spark_df.columns
cols.remove("id")
cols.insert(0, "id")
spark_df = spark_df.select(cols)

# αφαίρεση της Ε7 δεκαδικής ακρίβειας
for year_col in year_columns:
    spark_df = spark_df.withColumn(year_col, col(year_col).cast("decimal(11,0)"))

spark_df.show(spark_df.count(), truncate=False)

# Ερωτημα 3.1 

year_columns = [str(year) for year in range(2007, 2015)]
# Βρίσκω τον μέσο όρο των στηλών για κάθε χρονο

average_columns = [col(column) for column in year_columns]
average_column = sum(average_columns) / len(average_columns)
# Βάζω το GEO/TIME στην group by για να βρω τον μέσο όρο των χωρών

result = spark_df.select("GEO/TIME", average_column.alias("AverageTourists")) \
    .groupBy("GEO/TIME").avg("AverageTourists")

# Αποτέλεσμα 3.1

# Ακρίβεια τρίων δεκαδικών ψηφίων
result = result.withColumn("avg(AverageTourists)", col("avg(AverageTourists)").cast("decimal(11,3)"))

result.show(truncate=False)

# Ερώτημα 3.2

def compare_tourist_counts(countries):
    # Get the columns representing years
    year_columns = spark_df.columns[1:]  # Exclude the first column which should be the country names

    # Collect the country rows as a list
    data_rows = spark_df.collect()

    # Initialize a dictionary to store the results
    result = {country: [] for country in countries}

    # Compare tourist counts for each selected country against Greece
    for country in countries:
        country_row = [row for row in data_rows if row[0] == country]

        if country_row:
            country_row = country_row[0]
            for idx, year in enumerate(year_columns):
                year_val = int(year)  # Convert column names to integers for comparison
                greece_val = int([row for row in data_rows if row[0] == "Greece"][0][idx + 1])

                if country_row[idx + 1] < greece_val:  # Compare if the country value is less than Greece
                    result[country].append(year_val)

    return result

# Έβαλα τις πρώτες 5 χώρες
selected_countries = ["Belgium", "Bulgaria", "Czech Republic", "Denmark", "Germany (until 1990 former territory of the FRG)"]
result = compare_tourist_counts(selected_countries)

# Print the years where Greece had higher tourist counts than the selected countries
for country, years in result.items():
    if len(years) > 0:
        print(f"Για {len(years)} χρόνια, Η Ελλάδα είχε αριθμό διανυκτερεύσεων μεγαλύτερο απο αυτην την χώρα '{country}' , Οι συγκεκριμένες χρονιές: {years}")
    else:
        print(f"Η Ελλάδα δεν ειχε ποτε μεγαλύτερο αριθμό διανυκτερεύσεων απο την χώρα '{country}'")