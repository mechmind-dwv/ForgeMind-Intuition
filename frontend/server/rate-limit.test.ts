import { createServer, type Server } from "node:http";
import { afterEach, describe, expect, it } from "vitest";
import { createApp } from "./index";

const servers: Server[] = [];

afterEach(async () => {
  await Promise.all(
    servers.splice(0).map(
      server =>
        new Promise<void>((resolve, reject) => {
          server.close(error => (error ? reject(error) : resolve()));
        }),
    ),
  );
});

describe("Express request limits", () => {
  it("limits repeated SPA fallback requests", async () => {
    const server = createServer(createApp());
    servers.push(server);
    await new Promise<void>((resolve, reject) => {
      server.once("error", reject);
      server.listen(0, "127.0.0.1", () => resolve());
    });
    const address = server.address();
    if (!address || typeof address === "string") throw new Error("server did not bind");
    const url = `http://127.0.0.1:${address.port}/unknown-route`;

    let lastStatus = 0;
    for (let request = 0; request < 121; request += 1) {
      lastStatus = (await fetch(url)).status;
    }

    expect(lastStatus).toBe(429);
  });
});
