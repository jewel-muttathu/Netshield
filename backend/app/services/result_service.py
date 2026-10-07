from collections import Counter


def create_results(
    labels,
    confidence,
):

    predictions = []

    for label, conf in zip(
        labels,
        confidence,
    ):

        predictions.append(
            {
                "label": str(label),
                "confidence": float(conf),
            }
        )


    # Count how many flows belong
    # to each predicted class.

    counts = Counter(labels)


    summary = {
        str(label): int(count)
        for label, count in counts.items()
    }


    return {
        "total_flows": len(predictions),
        "summary": summary,
        "predictions": predictions,
    }