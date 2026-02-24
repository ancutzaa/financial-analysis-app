import os
import pandas as pd
from scipy.io import arff
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score
import joblib


def load_uci_data(folder_path):
    all_data = []

    for i in range(1, 6):
        file_name = f"{i}year.arff"
        file_path = os.path.join(folder_path, file_name)

        if os.path.exists(file_path):
            print(f"Se încarca {file_name}...")
            data, meta = arff.loadarff(file_path)
            df = pd.DataFrame(data)
            all_data.append(df)
        else:
            print(f"Fisierul {file_name} nu a fost gasit la calea {file_path}")

    if not all_data:
        raise FileNotFoundError("Nu s-a putut încarca niciun fișier .arff!")

    full_df = pd.concat(all_data, ignore_index=True)

    full_df['class'] = full_df['class'].str.decode('utf-8').astype(int)

    return full_df


def train_model():
    base_dir = os.getcwd()
    data_path = os.path.join(base_dir, 'backend', 'data', 'uci_polish_data')
    save_path = os.path.join(base_dir, 'backend', 'media', 'ml_models', 'polish_bankruptcy_v1.joblib')

    try:
        df = load_uci_data(data_path)
        print(f"Date încărcate. Total rânduri: {len(df)}")
    except Exception as e:
        print(f"Eroare la încărcare: {e}")
        return

    df = df.fillna(df.mean())

    X = df.drop(columns=['class'])
    y = df['class']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("Antrenam modelul Random Forest (100 de arbori)...")
    model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)

    print("-" * 30)
    print(f"PERFORMANTA MODEL:")
    print(f"Acuratete: {acc:.4f} (Cat de des ghicește corect)")
    print(f"F1-Score:  {f1:.4f} (Echilibrul intre precizie si identificarea falimentelor)")
    print("-" * 30)

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    joblib.dump(model, save_path)
    print(f"Model salvat în: {save_path}")


if __name__ == "__main__":
    train_model()