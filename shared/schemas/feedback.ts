export type FeedbackRating = "thumbs_up" | "thumbs_down";

export type FeedbackRequest = {
  message_id: number;
  rating: FeedbackRating;
  tags?: string[];
  rewrite_text?: string;
};

export type FeedbackResponse = {
  status: "ok" | "error";
};
