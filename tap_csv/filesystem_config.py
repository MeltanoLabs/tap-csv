"""JSON Schema for each filesystem configuration."""

from __future__ import annotations

from singer_sdk import typing as th  # JSON schema typing helpers

FTP = th.Property(
    "ftp",
    th.ObjectType(
        th.Property(
            "host",
            th.StringType,
            required=True,
            description="FTP server host",
        ),
        th.Property(
            "port",
            th.IntegerType,
            default=21,
            description="FTP server port",
        ),
        th.Property(
            "username",
            th.StringType,
            description="FTP username",
        ),
        th.Property(
            "password",
            th.StringType,
            secret=True,
            description="FTP password",
        ),
        th.Property(
            "encoding",
            th.StringType,
            default="utf-8",
            description="FTP server encoding",
        ),
    ),
    description="FTP connection settings",
)

GITHUB = th.Property(
    "github",
    th.ObjectType(
        th.Property(
            "org",
            th.StringType,
            required=True,
            description=("GitHub organization or user where the repository is located"),
        ),
        th.Property(
            "repo",
            th.StringType,
            required=True,
            description="GitHub repository",
        ),
        th.Property(
            "username",
            th.StringType,
            required=False,
            description="GitHub username",
        ),
        th.Property(
            "token",
            th.StringType,
            required=False,
            secret=True,
            description="GitHub token",
        ),
    ),
    description="GitHub connection settings",
)

DROPBOX = th.Property(
    "dropbox",
    th.ObjectType(
        th.Property(
            "token",
            th.StringType,
            secret=True,
            required=True,
            description="Dropbox token",
        ),
    ),
    description="Dropbox connection settings",
)
