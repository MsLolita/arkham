import random
import time
import traceback
from concurrent.futures import ThreadPoolExecutor

from core.utils import shift_file, logger
from core.utils.auto_generate.wallets import generate_random_wallets
from core.utils import file_to_list
from core.arkham import Arkham

from data.config import (
    REFERRAL_EMAIL, THREADS, CUSTOM_DELAY, EMAILS_FILE_PATH, PROXIES_FILE_PATH, WALLETS_FILE_PATH
)


class AutoReger:
    def __init__(self):
        self.emails_path: str = EMAILS_FILE_PATH
        self.proxies_path: str = PROXIES_FILE_PATH
        self.wallets_path: str = WALLETS_FILE_PATH

        self.success: int = 0

    def get_accounts(self) -> list[tuple[str, str, str, str | None]]:
        emails: list[str] = file_to_list(self.emails_path)
        wallets: list[str] = file_to_list(self.wallets_path)
        proxies: list[str] = file_to_list(self.proxies_path)

        min_accounts_len = len(emails)

        if not emails:
            logger.info("No emails!")
            exit()

        if not wallets:
            logger.info("Generated random wallets!")
            wallets = [wallet[0] for wallet in generate_random_wallets(min_accounts_len)]

        accounts = []

        for i in range(min_accounts_len):
            email, imap_pass = emails[i].split(":")[:2]
            accounts.append((email, imap_pass, wallets[i], proxies[i] if len(proxies) > i else None))

        return accounts

    def remove_account(self) -> None:
        shift_file(self.emails_path)
        shift_file(self.wallets_path)
        shift_file(self.proxies_path)

    def start(self) -> None:
        Arkham.referral = REFERRAL_EMAIL

        accounts = self.get_accounts()

        with ThreadPoolExecutor(max_workers=THREADS) as executor:
            executor.map(self.register, accounts)

        if self.success:
            logger.success(f"Successfully registered {self.success} accounts :)")
        else:
            logger.warning("No accounts registered :(")

    def register(self, account: tuple[str, str, str, str]) -> None:
        arkham = Arkham(*account)
        is_ok = False

        try:
            self.custom_delay()

            if arkham.send_verify_code():
                verify_code = arkham.get_verify_code()

                is_registered = arkham.sign_up(verify_code)

                if is_registered:
                    is_ok = arkham.connect_wallet()
        except Exception as e:
            logger.error(f"Error {e}")
            logger.debug(f"Error {e} | {traceback.format_exc()}")

        self.remove_account()

        if is_ok:
            arkham.logs("success", " | Registered")
            self.success += 1
        else:
            arkham.logs("fail")

    @staticmethod
    def custom_delay() -> None:
        if CUSTOM_DELAY[1] > 0:
            sleep_time = random.uniform(CUSTOM_DELAY[0], CUSTOM_DELAY[1])
            logger.info(f"Sleep for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)

