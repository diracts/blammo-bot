import pandas as pd
import random, logging

from log.loggers.custom_format import CustomFormatter  # for level colors

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter1 = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s : %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
)
file_handler = logging.FileHandler("logs.log")
file_handler.setFormatter(formatter1)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(CustomFormatter())

logger.addHandler(file_handler)
logger.addHandler(stream_handler)


class PointData:
    def __init__(self, path="../blammo-bot-private/user_data.csv"):
        self.path = path
        self.df = pd.read_csv(path, index_col=False, header=0)

    def _write_df(self):
        # writes the self.df object to the path
        self.df.to_csv(self.path, index=False)

    def _validate_user(self, username: str):
        username = username.lower()
        if username not in self.df["username"].values:
            new_row = pd.DataFrame(
                [[username, 0, 0]], columns=["username", "points", "gamble_loss"]
            )
            self.df = pd.concat([self.df, new_row], ignore_index=True)
            self._write_df()
        else:
            # user already exists
            pass

    def _user_points(self, username: str):
        # returns the number of points a user has, with no validation
        username = username.lower()
        return self.df.loc[self.df["username"] == username]["points"].values[0]

    def _user_gamble_loss(self, username: str):
        # returns the total accumulated gambling loss of a user, with no validation
        username = username.lower()
        return self.df.loc[self.df["username"] == username]["gamble_loss"].values[0]

    def add_points(self, username: str, num: int):
        # add num points to user in the user_data.csv file
        username = username.lower()
        self._validate_user(username)
        if num < 0:  # cannot have negative num
            logging.warning(f"Prevented add negative points to {username}. (num={num})")
            return
        points = self._user_points(username)
        points_new = points + num
        self.df.loc[self.df["username"] == username, "points"] = points_new
        self._write_df()
        logger.info(f"Added {num} points to {username}")

    def add_gamble_loss(self, username: str, num: int):
        # add num points to user in the user_data.csv file
        username = username.lower()
        self._validate_user(username)
        if num < 0:  # cannot have negative num
            logging.warning(
                f"Prevented add negative gamble loss to {username}. (num={num})"
            )
            return
        gamble_loss = self._user_gamble_loss(username)
        gamble_loss_new = gamble_loss + num
        self.df.loc[self.df["username"] == username, "gamble_loss"] = gamble_loss_new
        self._write_df()
        logger.info(f"Added {num} gamble loss to {username}")
        logger.debug(f"New gamble loss: {gamble_loss_new}")

    def sub_points(self, username: str, num: int):
        # subtract points from user in the user_data.csv file
        username = username.lower()
        self._validate_user(username)
        points = self._user_points(username)
        if num < 0:  # cannot have negative num
            logging.warning(
                f"Prevented subtract negative points from {username}. (num={num})"
            )
            return

        points_new = points - num
        if points_new < 0:
            points_new = 0  # cannot have negative points, so hard floor at 0
            logging.warning(
                f"Prevented {username} from having negative points. \
Tried to subtract {num} points from balance of {points}. Balance set to 0."
            )

        self.df.loc[self.df["username"] == username, "points"] = points_new
        self._write_df()
        logger.info(f"Subtracted {num} points from {username}.")

    def get_points(self, username: str):
        """Returns the number of points a user has.

        Args:
            username (str): username to check

        Returns:
            int: balance of user
        """
        username = username.lower()
        # return points from user in the user_data.csv file
        self._validate_user(username)
        points = self._user_points(username)
        if points < 0:
            logger.error(f"{username} has negative points ({points}). Forbidden.")
        if isinstance(points, float) or isinstance(points, str):
            points = int(points)

        return points

    def transfer(self, sender: str, receiver: str, amount: int):
        sender = sender.lower()
        receiver = receiver.lower()

        self._validate_user(sender)
        self._validate_user(receiver)
        sender_bal = self.get_points(sender)
        receiver_bal = self.get_points(receiver)
        if amount <= 0:
            logger.warning(
                f"Prevented transfer of {amount} points from {sender} to {receiver}. Amount cannot be <= 0."
            )
            logger.debug(f"sender bal: {sender_bal}, receiver bal: {receiver_bal}")
            return "invalid amount"

        initial_bal = sender_bal + receiver_bal
        if sender_bal < amount:
            logger.warning(
                f"Prevented transfer of {amount} points from {sender} to {receiver}. Sender has insufficient balance."
            )
            logger.debug(f"sender bal: {sender_bal}, receiver bal: {receiver_bal}")
            return "not enough points"

        if sender == receiver:
            logger.warning(
                f"Prevented transfer of {amount} points from {sender} to {receiver}. Cannot transfer to self."
            )
            logger.debug(f"sender bal: {sender_bal}, receiver bal: {receiver_bal}")
            return "cannot transfer to self"

        if sender_bal < 0 or receiver_bal < 0:
            logger.error(
                f"Prevented transfer of {amount} points from {sender} to {receiver}. Sender or receiver has \
negative balance. {sender} sender bal: {sender_bal}, {receiver} receiver bal: {receiver_bal}"
            )
            return "negative points"

        self.sub_points(sender, amount)
        self.add_points(receiver, amount)

        final_bal = self.get_points(sender) + self.get_points(receiver)
        if initial_bal != final_bal:
            logger.error(
                f"Problem transfering {amount} points from {sender} to {receiver}. Initial balance sum ({initial_bal}) \
does not match final balance sum ({final_bal}). Forbidden."
            )
            logger.info(f"Attempting to revert changes...")
            # revert changes
            self.add_points(sender, amount)
            self.sub_points(receiver, amount)
            if self.get_points(sender) + self.get_points(receiver) == initial_bal:
                logger.info(f"Successfully reverted changes.")
                return "balance mismatch"
            else:
                logger.error(
                    f"Could not revert changes. Final balance sum ({self.get_points(sender) + self.get_points(receiver)})"
                )
                return "balance mismatch and could not revert"
        else:
            logger.info(
                f"Successfully transfered {amount} points from {sender} to {receiver}."
            )
            return "success"

    def gamble(self, username: str, wager: int, fmt: str, win_odds: float = 0.50):
        if fmt not in ["points", "percent", "all"]:
            raise ValueError(
                f'fmt must be one of ["points", "percent", "all"], not {fmt}'
            )

        if win_odds < 0 or win_odds > 1:
            raise ValueError(f"win_odds must be between 0 and 1, not {win_odds}")

        username = username.lower()
        points = self.get_points(username)
        if points == 0:
            return "not enough points", points, 0

        if fmt == "points":
            if points < wager:
                return "not enough points", points, 0

            outcome = random.choices(["win", "lose"], weights=[win_odds, 1 - win_odds])[
                0
            ]
            if outcome == "win":
                self.add_points(username, wager)
                return "win", points + wager, wager
            elif outcome == "lose":
                self.sub_points(username, wager)
                self.add_gamble_loss(username, wager)
                return "lose", points - wager, wager

        elif fmt == "percent":
            wager = int(0.01 * wager * points)
            if points < wager:
                return "not enough points", points, 0
            if wager == 0:
                return "not enough points", points, 0

            outcome = random.choices(["win", "lose"], weights=[win_odds, 1 - win_odds])[
                0
            ]
            if outcome == "win":
                self.add_points(username, wager)
                return "win", points + wager, wager
            elif outcome == "lose":
                self.sub_points(username, wager)
                self.add_gamble_loss(username, wager)
                return "lose", points - wager, wager

        elif fmt == "all":
            wager = points
            outcome = random.choices(["win", "lose"], weights=[win_odds, 1 - win_odds])[
                0
            ]
            if outcome == "win":
                self.add_points(username, wager)
                return "win", points + wager, wager
            elif outcome == "lose":
                self.sub_points(username, wager)
                self.add_gamble_loss(username, wager)
                return "lose", points - wager, wager

        else:
            logger.error(f"Invalid format in gamble function: {fmt}")
            pass

    def get_top_points(self, ntop: int = 5):
        # return top users in the user_data.csv file
        sorted = self.df.sort_values(by="points", ascending=False).head(ntop)
        return list(sorted["username"]), list(sorted["points"])

    def get_top_gamble_loss(self, ntop: int = 5):
        # return top users in the user_data.csv file
        sorted = self.df.sort_values(by="gamble_loss", ascending=False).head(ntop)
        return list(sorted["username"]), list(sorted["gamble_loss"])

    def get_rank(self, username: str) -> tuple:
        """
        Outputs a tuple of ints specifying the users point and gamble loss rank.
        """
        logger.debug(f"Specificed username in get_rank: {username}")
        self._validate_user(username)
        self.df["loss_rank"] = self.df["gamble_loss"].rank(ascending=0)
        self.df["points_rank"] = self.df["points"].rank(ascending=0)
        index = self.df.index[self.df["username"] == username].tolist()
        points_rank = int(self.df.iloc[index]["points_rank"])
        loss_rank = int(self.df.iloc[index]["loss_rank"])
        return points_rank, loss_rank
