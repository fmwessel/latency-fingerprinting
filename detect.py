def compute_baseline(rtts):
    if len(rtts) < 2:
        raise ValueError("At least two RTT samples required")
    mean = sum(rtts) / len(rtts)
    variance = sum((x - mean) ** 2 for x in rtts) / (len(rtts) - 1)
    std_dev = variance ** 0.5

    return mean, std_dev

def is_anomalous(rtt, mean, std_dev, threshold=2.0):
    if std_dev == 0:
        return False
    
    deviation = abs(rtt - mean)
    return deviation > threshold * std_dev
