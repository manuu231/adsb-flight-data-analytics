#!/usr/bin/env python3
import os, json, datetime
folder = "datalog/"

# query 1 Range
q1_start = datetime.datetime(2018, 5, 6, 16, 0, 0)
q1_end   = datetime.datetime(2018, 5, 6, 18, 0, 0)

# query 2 Range
q2_start = datetime.datetime(2018, 5, 5, 16, 0, 0)
q2_end   = datetime.datetime(2018, 5, 7, 16, 0, 0)

q1 = []
q3 = []
s, c = 0, 0   

for f in os.listdir(folder):
    with open(os.path.join(folder, f)) as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if rec.get("type") != "print_reading":
                continue

            ts = datetime.datetime.strptime(rec["pitime"].replace("T"," "), "%Y-%m-%d %H:%M:%S.%f")

            # query 1
            if q1_start < ts < q1_end:
                row = {
                    "pitime": ts.strftime("%Y-%m-%d %H:%M:%S"),
                    "temp_5": rec.get("temp_5"),
                    "temp_8": rec.get("temp_8")
                }
                q1.append(row)

                # query 3 subset
                if rec.get("temp_8") and float(rec["temp_8"]) > 70:
                    q3.append(row)

            # query 2
            if q2_start < ts < q2_end and rec.get("temp_8"):
                s += float(rec["temp_8"])
                c += 1

print("Query 1 (all rows):")
for r in q1:
    print(r)
print("Total Q1 rows:", len(q1), "\n")

if c > 0:
    print("Query 2 (avg temp_8):", s / c, "\n")
else:
    print("Query 2: no data\n")

print("Query 3 (subset temp_8 > 70):")
for r in q3:
    print(r)
print("Total Q3 rows:", len(q3))
