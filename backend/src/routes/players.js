import express from "express";

import {
  getPlayers
} from "../services/playerService.js";

const router = express.Router();

router.get(
  "/",
  async (req, res) => {
    const players = await getPlayers();

    res.json(players);
  }
);

export default router;
