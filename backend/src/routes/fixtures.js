import express from "express";

import {
  getFixtures
} from "../services/fixtureService.js";

const router = express.Router();

router.get(
  "/",
  async (req, res) => {
    const fixtures = await getFixtures();

    res.json(fixtures);
  }
);

export default router;
