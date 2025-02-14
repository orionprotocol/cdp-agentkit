"""Util that calls Twitter API."""

from typing import Any

from cdp_agentkit_core.actions.social.twitter import (
    account_details,
    post_tweet,
)
from langchain_core.utils import get_from_dict_or_env
from pydantic import BaseModel, model_validator


class TwitterApiWrapper(BaseModel):
    """Wrapper for Twitter API."""

    client: Any | None = None

    @model_validator(mode="before")
    @classmethod
    def validate_environment(cls, values: dict) -> Any:
        """Validate that Twitter access token, token secret, and tweepy exists in the environment."""
        api_key = get_from_dict_or_env(values, "twitter_api_key", "TWITTER_API_KEY")
        api_secret = get_from_dict_or_env(values, "twitter_api_secret", "TWITTER_API_SECRET")
        access_token = get_from_dict_or_env(values, "twitter_access_token", "TWITTER_ACCESS_TOKEN")
        access_token_secret = get_from_dict_or_env(values, "twitter_access_token_secret", "TWITTER_ACCESS_TOKEN_SECRET")

        try:
            import tweepy
        except Exception:
            raise ImportError(
                "Tweepy Twitter SDK is not installed. " "Please install it with `pip install tweepy`"
            ) from None

        client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret,
        )

        values["client"] = client
        values["api_key"] = api_key
        values["api_secret"] = api_secret
        values["access_token"] = access_token
        values["access_token_secret"] = access_token_secret

        return values

    def account_details_wrapper(self) -> str:
        """Get the authenticated Twitter (X) user account details.

        Returns:
            str: A message containing account details for the authenticated user context in JSON format.

        """
        return account_details(client=self.client)

    def post_tweet_wrapper(self, tweet: str) -> str:
        """Post tweet to Twitter.

        Args:
            client (tweepy.Client): The tweepy client to use.
            tweet (str): The text of the tweet to post to twitter. Tweets can be maximum 280 characters.

        Returns:
            str: A message containing the result of the post action and the tweet.

        """
        return post_tweet(client=self.client, tweet=tweet)

    def run(self, mode: str, **kwargs) -> str:
        """Run the action via the Twitter API."""
        if mode == "account_details":
            return self.account_details_wrapper()
        elif mode == "post_tweet":
            return self.post_tweet_wrapper(**kwargs)
        else:
            raise ValueError("Invalid mode: " + mode)

