# NameTagPrinter

**NOTICE:** This is not production software! Security was not a concern when developing and will be implemented if 

This project allows for printing hackerspace themed nametags or badges via cups compatible label printer.
it is tested with a Brother QL-820NWBc, which is picked up by cups natively.

The project exposes a ZeroMQ socket on tcp port 6660 by default and is using the REQ/REP pattern.
For copyright reasons assets like hackerspace logos and fonts cannot be shipped with the project, but i was using an outline version of my home hackerspace (flipdot) and Jetbrains Mono as my default font for the name.

As most thermal label printers don't allow reliable, high quality grayscale images, you would most likely want to find an outlined or solid black and white version of your logo.

The project includes printing receipts for every nametag too. the receipt should copntain the name and hackerspace for the user and a QR-Code to replicate the badge if it breaks or the user changes clothes.

## Protocol

The protocol is pretty simple. It should be sent as a String with the following pattern:

```
COMMAND;PARAM1;PARAM2;...
```

The currently supported commands are:
- `TAG` for printing the nametag on the label printer
- `RECEIPT` for printing the receipt of a single nametag
- `STATS` for printing the statistics which spaces, how many Badges and how many badges per space
- `RESET` for resetting the stat counters

## Parameters

Each command can have a different number of parameters. I'll list them here:
- `TAG;name;space;logo,url`
  - The `name` parameter is the user's chosen Nickname to be written as text on the Badge
  - The `space` parameter is for identifying the hackerspace. it is mainly intended for stats, but can be printed instead of the logo if said logo is empty.
  - The `logo` parameter is the filename of the logo that should be used. I am using the filename, so one could add better logos without causing problems on older jobs.
  - The `url` parameter contains the url ti the hackerspace website. It will be printed as a QR-Code on the tag, but can be blank if none should be printed.
- `RECEIPT;name;space;logo;url`
  - The `name` parameter is the user's chosen Nickname to be written as text on the Badge
  - The `space` parameter is for identifying the hackerspace. It will be printed on the receipt for reference. It can be left blank `UNKNOWN` will be printed instead.
  - The `logo` parameter is the filename of the logo that should be used. I am using the filename, so one could add better logos without causing problems on older jobs.
  - The `url` parameter contains the url ti the hackerspace website. It will be printed as a QR-Code on the tag, but can be blank if none should be printed.
- `STATS`
  - This command does not have any parameters yet. It will gain a parameter to get statistics of a batch job if batch jobs are properly implemented.
- `RESET`
  - This command does not have any parameters yet.

## ZeroMQ

ZeroMQ is a standard and libraries for many different languages that allows interoperation between different languages.
It is centered around an abstract notion of sockets that can use a number of transports under the hood. In this case tcp is used, but IPC would be faster.
ZeroMQ has different messaging patterns that are implemented by the sockets. in this case the Request/Reply pattern is used.

This means that the server implements a Reply socket. Request sockets can send requests and have to receive an answer as the next message.
Reasons for choosing this pattern was the bidirectional nature and the option to block a frontend application until a job is completed.