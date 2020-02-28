# Examples for skale.py

These are examples of skale.py usage. 

There are two main parts:

-   nodes.py - set of CLI commands for managing SKALE nodes
-   schains.py - set of CLI commands for managing SKALE schains


## Nodes.py

To check available commands you can execute:

```bash
python nodes.py --help 
```

Nodes.py has following commands and options

    Usage: nodes.py [OPTIONS] COMMAND [ARGS]...

    Options:
      --endpoint TEXT      SKALE manager endpoint
      --abi-filepath PATH  ABI file
      --help               Show this message and exit.

    Commands:
      create           Command to create given amount of nodes
      remove           Command to remove node spcified by name
      schains-by-node  Command that shows schains for active nodes
      show             Command to show active nodes

-   endpoint parameter use value of ENDPOINT env variable by default 
-   abi-filepath parameter use value of ABI_FILEPATH env variable by default 

Nodes.py command usage examples:

```bash
python nodes.py create 12 --abi-filepath ~/abi-file
```

```bash
python nodes.py remove GNGLL11F
```

```bash
python nodes.py show
```

```bash
python nodes.py schains-by-node --save-to ~/dir
```

## Schains.py

To check available commands you can execute:

```bash
python schians.py --help 
```

Schains.py has the following commands and options

    Usage: schains.py [OPTIONS] COMMAND [ARGS]...

    Options:
      --endpoint TEXT      SKALE manager endpoint
      --abi-filepath TEXT  ABI file
      --help               Show this message and exit.

    Commands:
      create  Command that creates new accounts with schains
      remove  Command that removes schain by name
      show    Command that show all schains ids

endpoint and abi-filepath parameter has the same meaning as in nodes.py

Schain.py command usage examples:

```bash
python schains.py create --eth-amount 100 --skale-amount 1230 --save-to creds
```

```bash
python schains.py show
```

```bash
python schains.py remove node-name
```

## Validation.py

To check available commands you can execute:

```bash
python validation.py --help
```

Validation.py has the following commands and options

    Usage: validation.py [OPTIONS] COMMAND [ARGS]...

    Options:
      --endpoint TEXT      Skale manager endpoint
      --abi-filepath PATH  abi file
      --help               Show this message and exit.

    Commands:
      accept-request            Accept delegation specified by id
      delegate                  Delegate tokens to validator specified by id
      delegations-by-holder     Show delegations by holder
      delegations-by-validator  Show delegations by validator
      ls                        Show information about validators
      register                  Register validator
    Commands that can be preformed only by owner:
      set-msr                   Set minimum stacking amount (owner only...
      skip-delay                Skip delegation delay specified by delegation id
      trusted                   Check if validator specified by id trused
      whitelist                 Add validator specified by id to whitelist

endpoint and abi-filepath parameter has the same meaning as in nodes.py

Validation.py command usage examples:

```bash
python validation.py register test-validator
```

```bash
python validation.py ls
```

```bash
python validation.py whitelist 1
```
