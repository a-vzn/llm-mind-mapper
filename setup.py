from setuptools import setup, find_packages

setup(
    name="llm_mind_mapper",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "streamlit",
        "pyvis",
        "langchain-ollama",
        "langchain",
        "langchain-core",
        "pydantic",
        "pytest",
        "requests",
    ],
    author="Aviral Somani",
    description="A mind mapping tool that uses LLMs to analyze conversations",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/aviralsomani/llm-mind-mapper",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
)
