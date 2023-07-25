import os


class Cox:
    """
       An Coxian Distribution.

       Attributes:
            lambda0 (float): The lambda0 of the distribution.
            lambda1 (float): The lambda1 of the distribution.
            p0 (float): The p0 of the distribution.
       """

    def __init__(self, lambda0, lambda1, p0):
        """
            The constructor for a Coxian Distribution.

            Parameters:
                lambda0 (float): The lambda0 of the distribution.
                lambda1 (float): The lambda1 of the distribution.
                p0 (float): The p0 of the distribution.
        """
        self.lambda0 = lambda0
        self.lambda1 = lambda1
        self.p0 = p0


class Det:
    """
       A Deterministic Distribution.

       Attributes:
            k (float): The k of the distribution.
       """

    def __init__(self, k):
        """
            The constructor for a deterministic Distribution.

            Parameters:
                k (float): The k of the distribution.
        """
        self.k = k


class Disabled:
    """
       A Disabled service distribution.

       """

    def __init__(self):
        """
            The constructor for a Disabled Distribution.

        """


class Erlang:
    """
    An Erlang Distribution.

    Attributes:
        lambda_value (float): The lambda of the distribution.
        k (int): The k of the distribution.
    """

    def __init__(self, lambda_value, k):
        """
        The constructor for an Erlang Distribution.

        Parameters:
            lambda_value (float): The lambda of the distribution.
            k (int): The k of the distribution.
        """
        self.lambda_value = lambda_value
        self.k = k

    @staticmethod
    def fitMeanAndSCV(mean, scv):
        """
        Fits the parameters of the distribution given the mean and the squared coefficient of variation.

        Parameters:
            mean (float): The mean of the distribution.
            scv (float): The squared coefficient of variation of the distribution.

        Returns:
            Erlang: An Erlang distribution fitted to the given parameters.
        """
        k = 1 / scv
        lamda_value = k / mean
        return Erlang(lamda_value, int(k))

    @staticmethod
    def fitMeanAndOrder(mean, order):
        """
        Fits the parameters of the distribution given the mean and the order.

        Parameters:
            mean (float): The mean of the distribution.
            order (int): The order of the distribution.

        Returns:
            Erlang: An Erlang distribution fitted to the given parameters.
        """
        r = order
        alpha = order / mean
        return Erlang(alpha, r)


class Exp:
    """
       An Exponential Distribution.

       Attributes:
            lambda_value (float): The lambda of the distribution.
       """

    def __init__(self, lambda_value):
        """
            The constructor for an exponential Distribution.

            Parameters:
                lambda_value (float): The lambda of the distribution.
        """
        self.lambda_value = lambda_value


class Gamma:
    """
    An Gamma Distribution.

    Attributes:
        alpha (float): The alpha of the distribution.
        theta (float): The theta of the distribution.
    """

    def __init__(self, alpha, theta):
        """
        The constructor for a Gamma Distribution.

        Parameters:
            alpha (float): The alpha of the distribution.
            theta (float): The theta of the distribution.
        """
        self.alpha = alpha
        self.theta = theta


class HyperExp:
    """
       An hyperexponential Distribution.

       Attributes:
            p (float): The p of the distribution.
            lambda1 (float): The lambda1 of the distribution.
            lambda2 (float): The lambda2 of the distribution.
       """

    def __init__(self, p, lambda1, lambda2):
        """
            The constructor for a hyperexponential Distribution.

            Parameters:
                p (float): The p of the distribution.
                lambda1 (float): The lambda1 of the distribution.
                lambda2 (float): The lambda2 of the distribution.
        """
        self.p = p
        self.lambda1 = lambda1
        self.lambda2 = lambda2


class Lognormal:
    """
    An Lognormal Distribution.

    Attributes:
        mu (float): The mu of the distribution.
        sigma (float): The sigma of the distribution.
    """

    def __init__(self, mu, sigma):
        """
        The constructor for a lognormal Distribution.

        Parameters:
            mu (float): The mu of the distribution.
            sigma (float): The sigma of the distribution.
        """
        self.mu = mu
        self.sigma = sigma


class Normal:
    """
    A Normal Distribution.

    Attributes:
        mean (float): The mean of the distribution.
        standard deviation (float): The standard deviation of the distribution.
    """

    def __init__(self, mean, standardDeviation):
        """
        The constructor for a normal Distribution.

        Parameters:
            mean (float): The mean of the distribution.
            standard deviation (float): The standard deviation of the distribution.
        """
        self.mean = mean
        self.standardDeviation = standardDeviation


class Pareto:
    """
    A Pareto Distribution.

    Attributes:
        mu (float): The mu of the distribution.
        sigma (float): The sigma of the distribution.
    """

    def __init__(self, alpha, k):
        """
        The constructor for a pareto Distribution.

        Parameters:
            alpha (float): The alpha of the distribution.
            k (float): The k of the distribution.
        """
        self.alpha = alpha
        self.k = k


class Replayer:
    """
    A class for replaying data from a file.

    Attributes:
        fileName (str): The path to the file to replay.
    """

    def __init__(self, fileName):
        """
        The constructor for the Replayer class.

        Parameters:
            fileName (str): The name of the file to replay.
        """
        self.fileName = os.getcwd() + "/" + fileName


class Uniform:
    """
    A Uniform Distribution.

    Attributes:
        min (float): The min of the distribution.
        max (float): The max of the distribution.
    """

    def __init__(self, min, max):
        """
        The constructor for a uniform Distribution.

        Parameters:
            min (float): The min of the distribution.
            max (float): The max of the distribution.
        """
        self.min = min
        self.max = max


class Weibull:
    """
    A Weibull Distribution.

    Attributes:
        lambda_value (float): The lambda of the distribution.
        k (float): The k of the distribution.
    """

    def __init__(self, lambda_value, k):
        """
       The constructor for a weibull Distribution.

       Parameters:
           lambda_value (float): The lambda of the distribution.
            k (float): The k of the distribution.
       """

        self.lambda_value = lambda_value
        self.k = k


class ZeroServiceTime:
    """
    A Zero Service time service distribution.

    """

    def __init__(self):
        """
       The constructor for a Zero Service time service Distribution.

       """

