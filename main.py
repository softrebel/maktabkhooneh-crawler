import click
import os
from src.handler import MaktabkhoonehCrawler
from src._core import project_configs
from src._core.utils import save_model_to_json, load_model_from_json
from src._core.schemas import CourseInfo


cookie_file = f"{project_configs.TEMP_PATH}{os.sep}maktabkhooneh_cookies"


@click.group()
def cli():
    """
    A simple command-line interface for interacting with Maktabkhooneh.
    """
    pass


@cli.command()
@click.option(
    "--save-cookies",
    is_flag=True,
    default=True,
    help="Force to save cookies.",
)
@click.option(
    "--output",
    required=False,
    type=str,
    default=f"{project_configs.TEMP_PATH}",
    help="Path to the output directory",
)
def login(save_cookies: bool, output: str):
    """Logs into Maktabkhooneh."""
    crawler = MaktabkhoonehCrawler(
        username=project_configs.MAKTABKHOONEH_USERNAME,
        password=project_configs.MAKTABKHOONEH_PASSWORD,
        cookies_file=cookie_file,
        save_path=output,
    )
    user_info = crawler.login(force_save_cookies=save_cookies)
    click.echo(f"Logged in as email:{user_info.email} phone:{user_info.phone}")
    click.echo(f"Logged into Maktabkhooneh. Cookies saved to {cookie_file}")


@cli.command()
@click.option(
    "--course-url",
    required=True,
    type=str,
    help="The url of the maktabkhooneh course",
)
@click.option(
    "--output",
    required=False,
    type=str,
    default=f"{project_configs.TEMP_PATH}",
    help="Path to the output directory",
)
def crawl(course_url: str, output: str):
    """Crawl and save course info to a json file based on course url"""
    crawler = MaktabkhoonehCrawler(
        username=project_configs.MAKTABKHOONEH_USERNAME,
        password=project_configs.MAKTABKHOONEH_PASSWORD,
        cookies_file=cookie_file,
        save_path=output,
    )
    crawler.init_cookies()
    if len(crawler.client.cookies.jar) == 0:
        click.echo("No Cookies. Please login first.")
        return
    course_info = crawler.crawl_course_link(course_url)
    if course_info:
        course_slug = course_info.course.slug
        file_name = f"{output}{os.sep}{course_slug}.json"
        save_model_to_json(model=course_info, filename=file_name)
        click.echo(f"Course info saved to {file_name}")
    else:
        click.echo(f"Could not fetch information about {course_url}")


@cli.command()
@click.option(
    "--input-file",
    required=True,
    type=str,
    help="Path to the JSON file containing course information.",
)
@click.option(
    "--max-threads",
    required=False,
    type=int,
    default=5,
    help="Max threads to use when downloading video",
)
@click.option(
    "--output",
    required=False,
    type=str,
    default=f"{project_configs.TEMP_PATH}",
    help="Path to the output directory",
)
def download(input_file: str, max_threads: int, output: str):
    """Loads course information from a JSON file and downloads videos for that course."""
    try:
        crawler = MaktabkhoonehCrawler(
            username=project_configs.MAKTABKHOONEH_USERNAME,
            password=project_configs.MAKTABKHOONEH_PASSWORD,
            cookies_file=cookie_file,
            save_path=output,
        )
        crawler.init_cookies()
        if len(crawler.client.cookies.jar) == 0:
            click.echo("No Cookies. Please login first.")
            return
        course_info = load_model_from_json(CourseInfo, input_file)
        crawler.download_course_videos(course_info, max_threads)
        click.echo(f"Finished downloading course videos from: {input_file}")
    except Exception as e:
        click.echo(f"Error downloading videos: {e}")


if __name__ == "__main__":
    cli()
