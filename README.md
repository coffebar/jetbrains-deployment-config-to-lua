# Convert JetBrains deployment config to lua

## Usage

```bash
$ python3 main.py ~/dev/idea-project
```

It will parse `~/dev/idea-project/.idea/` and generate `~/dev/idea-project/.nvim/deployment.lua`

```lua
-- example deployment.lua
return {
  ["server1"] = {
    host = "server1",
    username = "web",
    port = 9202,
    mappings = {
      {
        ["local"] = "domains/example.com",
        ["remote"] = "/var/www/example.com",
      },
    },
    excludedPaths = {
      "src",
    },
  },
}
```

Example [how this config can be used](https://github.com/coffebar/dotfiles/blob/b336aa5b985763237de6fbf9498cf147bbe6f162/.config/nvim/lua/coffebar/deployment.lua#L23C1-L67C4).

## DISCLAIMER

There are no guarantees that it will work for you.

This is not a complete solution, it's just a quick hack that works for my projects, where I use only ssh connections with key based auth.

Password based auth is not supported!
