# Retail Ops Agent

**A production-ready, agentic AI system built on AWS Lambda and Amazon Bedrock**  
This project demonstrates a fully autonomous AI agent capable of analyzing sales and inventory data, planning actions, and executing business decisions. Built with **LangGraph** and **LangChain**, deployed on **AWS Lambda**, and integrated with **Amazon Bedrock LLMs**.

---

## Features

- **Agentic AI Architecture**: Implements an **Analyze → Plan → Act** flow.
- **Tool Integration**: Connects to business functions such as inventory and sales analysis.
- **LLM-powered reasoning**: Uses Bedrock foundation models for decision-making.
- **Lambda-ready**: Runs entirely on AWS Lambda with proper IAM configuration.
- **Extensible**: Memory and state can be added using DynamoDB or other data stores.
- **Production-grade packaging**: Linux-compatible deployment with all dependencies.

---

## Architecture Overview

```text
[Sales & Inventory Tools] --> [Analyze Node] --> [Plan Node] --> [Act Node] --> [Decision Output]
          |                                                        |
          +--------------------------------------------------------+
                    LLM reasoning via Amazon Bedrock
