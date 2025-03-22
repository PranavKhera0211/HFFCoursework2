import pandas as pd
import matplotlib.pyplot as plt
from lab8 import df
from sklearn.model_selection import TimeSeriesSplit 

# Our data is already sorted in order by time


if "directional_change" not in df.columns:
    raise ValueError(" 'directional_change' column is missing! Run lab8.py first.")

train_size = int(len(df)*0.8)
train_df = df.iloc[:train_size].copy()
test_df = df.iloc[train_size:].copy()

def backtest_strategy(data):
    # Initialize Trading Strategy Variables 
    position_open = False
    position_type = None # long or short
    P_entry = None
    P_DCC_up = None
    take_profit_level = None
    stop_loss_level = None
    trades = []

    theta = 0.004  # Same theta used in lab8.py
    # Execute Trading Logic
    for index, row in data.iterrows():
        current_price = row["mid"]

        # Open trade if DC↑ occurs and no trade is open
        if row["directional_change"] == "DC↑" and not position_open:
            P_entry = current_price
            P_DCC_up = current_price
            take_profit_level = P_DCC_up * (1 + theta / 2)
            stop_loss_level = P_DCC_up * (1 - theta / 2)
            entry_time = row["datetime"]
            position_open = True
            position_type = "long"
        
        elif row["directional_change"] == "DC↓" and not position_open:
            P_entry = current_price
            P_DCC = current_price
            take_profit_level = P_DCC * (1 - theta / 2)  # Profit when price drops
            stop_loss_level = P_DCC * (1 + theta / 2)  # Stop loss when price rises
            entry_time = row["datetime"]
            position_open = True
            position_type = "short"

        # Exit trade if price hits take profit or stop loss
        elif position_open:
            if position_type == "long":
                if current_price >= take_profit_level or current_price <= stop_loss_level:
                    exit_price = current_price
                    exit_time = row["datetime"]
                    PnL = exit_price - P_entry  # Profit = Sell Price - Buy Price

                    trades.append({
                        "entry_time": entry_time,
                        "exit_time": exit_time,
                        "position_type": position_type,
                        "P_entry": P_entry,
                        "exit_price": exit_price,
                        "PnL": PnL
                    })

                    position_open = False

            elif position_type == "short":
                if current_price <= take_profit_level or current_price >= stop_loss_level:
                    exit_price = current_price
                    exit_time = row["datetime"]
                    PnL = P_entry - exit_price  # Profit = Sell Price - Buy Price (Short)

                    trades.append({
                        "entry_time": entry_time,
                        "exit_time": exit_time,
                        "position_type": position_type,
                        "P_entry": P_entry,
                        "exit_price": exit_price,
                        "PnL": PnL
                    })

                    position_open = False

    return pd.DataFrame(trades)

train_trades = backtest_strategy(train_df)
test_trades = backtest_strategy(test_df)





def evaluate_performance(trades_df, dataset_name="Dataset"):
    # Performance Analysis 
    total_trades = len(trades_df)
    total_profit = trades_df["PnL"].sum()
    win_rate = (trades_df["PnL"] > 0).mean() * 100
    avg_profit = trades_df["PnL"].mean()
    max_drawdown = trades_df["PnL"].min()

    long_trades = trades_df[trades_df["position_type"] == "long"]
    short_trades = trades_df[trades_df["position_type"] == "short"]

    # Print results
    print(f"Performance on {dataset_name}:")
    print(f"Total Trades: {total_trades}")
    print(f"Total PnL: {total_profit:.5f}")
    print(f"Win Rate: {win_rate:.2f}%")
    print(f"Average PnL per Trade: {avg_profit:.5f}")
    print(f"Max Drawdown (Largest Loss): {max_drawdown:.5f}")
    print("-" * 50)


    print("Breakdown:")
    print(f"Long Trades: {len(long_trades)}, PnL: {long_trades['PnL'].sum():.5f}")
    print(f"Short Trades: {len(short_trades)}, PnL: {short_trades['PnL'].sum():.5f}")
    print("=" * 50)

evaluate_performance(train_trades, "Training Set")
evaluate_performance(test_trades, "Testing Set")

# Save Results 
train_trades.to_csv("train_trading_results.csv", index=False)
test_trades.to_csv("test_trading_results.csv", index=False)

train_trades[train_trades["position_type"] == "long"].to_csv("train_long_trades.csv", index=False)
train_trades[train_trades["position_type"] == "short"].to_csv("train_short_trades.csv", index=False)

test_trades[test_trades["position_type"] == "long"].to_csv("test_long_trades.csv", index=False)
test_trades[test_trades["position_type"] == "short"].to_csv("test_short_trades.csv", index=False)