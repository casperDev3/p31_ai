"""Tests for local command handling — no network, no Groq calls."""

from voice_assistant.processor import commands


def test_exit_command_detected():
    assert commands.is_exit_command("вихід")
    assert commands.is_exit_command("Будь ласка, стоп.")
    assert commands.is_exit_command("quit")


def test_non_exit_phrase():
    assert not commands.is_exit_command("розкажи анекдот")


def test_time_command():
    assert "Зараз" in commands.handle("котра година зараз?")


def test_date_command():
    assert "Сьогодні" in commands.handle("яка дата сьогодні?")


def test_unknown_returns_none():
    assert commands.handle("яка столиця Франції") is None
