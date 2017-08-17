#!/usr/bin/env python
"""Provide error classes for holographer."""

# Imports
import logging
log = logging.getLogger(__name__)


# Metadata
__author__ = "Gus Dunn"
__email__ = "w.gus.dunn@gmail.com"




class HolographerError(Exception):

    """Base error class for holographer."""


class ValidationError(HolographerError):

    """Raise when a validation/sanity check comes back with unexpected value."""
