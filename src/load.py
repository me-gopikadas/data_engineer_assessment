import pandas as pd
from sqlalchemy import create_engine, text

class MySQLLoader:
    def __init__(self, user, password, host, database):
        connection_url = f"mysql+pymysql://{user}:{password}@{host}/{database}"
        self.engine = create_engine(connection_url)

    def run_sql_script(self, script_path):
        """Run SQL file (create tables, etc)"""
        with open(script_path, "r") as file:
            sql_commands = file.read()

        with self.engine.connect() as conn:
            for command in sql_commands.split(";"):
                cmd = command.strip()
                if cmd:
                    conn.execute(text(cmd))
        print("SQL script executed successfully!")


    def load_properties(self, props_df):
        """Load main properties table first"""
        props_df.to_sql("properties", self.engine, if_exists="append", index=False)
        print("properties loaded")

    def build_external_id_map(self):
        """Map external_id → property_id after inserting properties"""
        with self.engine.connect() as conn:
            rows = conn.execute(text("SELECT property_id, external_id FROM properties"))
            mapping = {row.external_id: row.property_id for row in rows}
        return mapping

    def add_property_id(self, df, mapping):
        """Add foreign key column to child tables"""
        if df.empty:
            return df
        df["property_id"] = df["external_id"].map(mapping)
        df = df[df["property_id"].notnull()]
        df = df.drop(columns=["external_id"], errors="ignore")
        return df

    def load_child_table(self, df, table_name):
        """Load any child table"""
        if not df.empty:
            df.to_sql(table_name, self.engine, if_exists="append", index=False)
            print(f"{table_name} loaded")
        else:
            print(f"{table_name} is empty, skipped")
