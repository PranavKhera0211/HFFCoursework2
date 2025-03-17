import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


class intrinsic_time:
    def __init__(self, delta_up, delta_down):
        self.delta_up = delta_up
        self.delta_down = delta_down
        self.S_ext = None
        self.S_IE = None
        self.mode = "up" 

    def detect_event(self, S_tick):
        if self.S_ext is None:
            self.S_ext = S_tick
            self.S_IE = S_tick
            return 0
        
    
        if self.mode == "up":
            if S_tick - self.S_ext >= self.delta_up:
                self.mode = "down"
                self.S_ext = S_tick
                self.S_IE = S_tick
                return 1
            elif S_tick < self.S_ext:
                self.S_ext = S_tick
                if self.S_IE - self.S_ext >= self.delta_down:
                    self.S_IE = S_tick
                    return -2
            return 0

        elif self.mode == "down":
            if self.S_ext - S_tick >= self.delta_down:
                self.mode = "up"
                self.S_ext = S_tick
                self.S_IE = S_tick
                return -1
            elif S_tick > self.S_ext:
                self.S_ext = S_tick
                if self.S_ext - self.S_IE >= self.delta_up:
                    self.S_IE = S_tick
                    return 2
            return 0
        
class directional_change:
    def __init__(self, theta):
        self.theta = theta
        self.P_EXT = None  # Extreme point
        self.mode = None  # Up or down trend

    def detect_dc(self, P_c):  # P_c is the current price
        if self.P_EXT is None:
            self.P_EXT = P_c
            return None  # No DC yet
        
        if self.mode == "up":
            if P_c <= self.P_EXT * (1 - self.theta):  # Downward DC
                self.mode = "down"
                self.P_EXT = P_c
                return "DC↓"
            self.P_EXT = max(self.P_EXT, P_c)  # Update extreme in up mode

        elif self.mode == "down":
            if P_c >= self.P_EXT * (1 + self.theta):  # Upward DC
                self.mode = "up"
                self.P_EXT = P_c
                return "DC↑"
            self.P_EXT = min(self.P_EXT, P_c)  # Update extreme in down mode

        return None  # No directional change

            

file_path = '/Users/Kherafamily/Documents/KCL/HFF/HFFCoursework2/cleaned_DAT_ASCII_EURGBP_T_202501.csv'
df = pd.read_csv(file_path, sep=',', header=None, names=["datetime", "bid", "ask", "mid"])


intrinsic_detector = intrinsic_time(delta_up = 0.00005, delta_down = 0.00005)
df["event"] = [intrinsic_detector.detect_event(mid) for mid in df["mid"]]

event_df = df[df["event"] != 0]

# regular plot

plt.figure(figsize=(12, 6))
plt.plot(event_df["datetime"], event_df["mid"], linestyle='-', linewidth = 1, color='blue', label="Intrinsic Events")

# X-axis formatting
plt.xticks([event_df["datetime"].iloc[0], event_df["datetime"].iloc[-1]])  # Rotate for better visibility

# Other formatting
plt.xlabel("Time")
plt.ylabel("Mid-Price")
plt.title("Intrinsic Time Events in EUR/GBP")
plt.legend()
plt.grid()

# Show the plot
plt.show()

# coloured plot

#plt.figure(figsize=(12, 6))
#plt.scatter(event_df["datetime"], event_df["mid"], c=event_df["event"], cmap='coolwarm', marker='o', label="Intrinsic Events")
#plt.xlabel("Time")
#plt.ylabel("Mid-Price")
#plt.title("Intrinsic Time Events in EUR/GBP")
#plt.colorbar(label="Event Type")  # Color bar to show event values (-2, -1, 1, 2)
#plt.grid()
#plt.xticks(rotation=45)
#plt.show()

print(event_df)
#print(df)
#print(df["event"].isnull().sum())
#print(df["event"].notnull().sum())
#print(df["event"].value_counts())  # Check distribution of event types
