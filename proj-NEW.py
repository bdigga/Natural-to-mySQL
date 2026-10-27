import mysql.connector
from google import genai

# 1. Login to MySQL Database
print("--- MYSQL DATABASE LOGIN ---")
h = input("Enter Host (e.g., localhost): ")
u = input("Enter User (e.g., root): ")
p = input("Enter Password: ")
d = input("Enter Database Name: ")

try:
    con = mysql.connector.connect(host=h, user=u, password=p, database=d)
    cur = con.cursor()
    print("Connected to MySQL successfully!\n")
except Exception as e:
    print("Login Failed:", e)
    exit()

# 2. Setup Google Gemini Free API
api_key = "AQ.Ab8RN6LbGmkPg1-J2YXa7YM9b-cCALlLFV3TKEDktSrH6pHfog"
client = genai.Client(api_key=api_key)

# 3. Main Program Loop
while True:
    text = input("\nEnter your query in plain English: ")

    # Short boilerplate prompt to save tokens and restrict to Class 12 SQL
    prompt = "Give ONLY raw MySQL query (no markdown, no explanation) using CBSE Class 12 SQL concepts for: " + text

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    # Clean output string
    sql = response.text.replace("```sql", "").replace("```", "").strip()
    print("\nGenerated SQL:", sql)

    # 4. Safety Guardrail Check
    clean_sql = sql.upper().replace(";", " ").replace("(", " ")
    words = clean_sql.split()

    unsafe_words = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE", "TRUNCATE"]
    is_safe = True

    # Must start with a read-only command
    if len(words) == 0 or words[0] not in ["SELECT", "SHOW", "DESC", "DESCRIBE"]:
        is_safe = False

    # Must not contain any modifying or deleting keywords
    for w in words:
        if w in unsafe_words:
            is_safe = False

    if is_safe == False:
        print("WARNING: Unsafe command detected! Altering, deleting, or creating data is not allowed.")
    else:
        # 5. Execute Safe SQL Query
        try:
            cur.execute(sql)
            rows = cur.fetchall()
            print("\n--- QUERY OUTPUT ---")
            for r in rows:
                print(r)
        except Exception as e:
            print("SQL Error:", e)

    # 6. Ask user whether to continue
    ans = input("\nDo you want to continue? (yes/no): ").lower().strip()
    if ans != "yes" and ans != "y":
        print("Exiting program.")
        break

cur.close()
con.close()
