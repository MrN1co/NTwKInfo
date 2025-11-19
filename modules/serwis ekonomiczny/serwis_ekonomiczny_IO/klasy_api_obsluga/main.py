from Manager import NBPApp as Manager

if __name__ == "__main__":
    app = Manager()

    # Aktualne dane
    rates, gold_price = app.update_all()
    print("Aktualne kursy walut (A+B):", list(rates.items())[:5])
    print("Aktualna cena złota:", gold_price)

    # Historyczne dane walut
    print("Pobieranie historycznych kursów walut (1 rok)...")
    df_rates = app.history.get_historical_rates_df(tables=["a"], years=1)
    print(df_rates.head())

    # Historyczne ceny złota
    print("Pobieranie historycznych cen złota (1 rok)...")
    df_gold = app.history.get_historical_gold_prices(years=1)
    print(df_gold.head())

    # Wykres dla USD
    app.plot_rates(df_rates, "USD")