import express from "express";

import {
  getPredictions
} from "../services/predictionService.js";

const router = express.Router();

router.get(
  "/today",
  async (req, res) => {

    const predictions =
      await getPredictions();

    res.json(predictions);
  }
);

export default router;