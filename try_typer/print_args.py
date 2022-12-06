import typer

greeting = typer.style("Hello", fg=typer.colors.GREEN, bg=typer.colors.WHITE, bold=True)

def main():
    typer.echo(f"{greeting} World")

if __name__ == "__main__":
    typer.run(main)
