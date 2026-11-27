#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# ZSH-native shibboleth (Rule 1)
typeset _ZSH_PURE=${(%):-%x}
#===============================================================================
# vde-check-pr-evidence.zsh - Pull request evidence check (Signet #778, second half)
#
# Reads the pull request body, author, head ref and head and base repositories from the environment only:
# VDE_PR_BODY, VDE_PR_AUTHOR, VDE_PR_HEAD_REF, VDE_PR_HEAD_REPO and VDE_PR_BASE_REPO. The body is DATA. It is never
# executed, evaluated or expanded as shell code.
#
#   exit 0  pass, or exempt (author dependabot[bot], or head ref exactly develop or stable from the same repository)
#   exit 1  a rule failed; the output names it as rule (a), (b), (c) or (d)
#   exit 2  usage error (any argument)
#===============================================================================

typeset -r PLACEHOLDER='(Paste terminal output here)'

main() {
    emulate -L zsh
    setopt localoptions extendedglob

    if (( $# > 0 )); then
        print -r -- "usage: vde-check-pr-evidence.zsh takes no arguments; it reads VDE_PR_BODY, VDE_PR_AUTHOR, VDE_PR_HEAD_REF, VDE_PR_HEAD_REPO and VDE_PR_BASE_REPO from the environment" >&2
        return 2
    fi

    local body="${VDE_PR_BODY-}"
    local author="${VDE_PR_AUTHOR-}"
    local head="${VDE_PR_HEAD_REF-}"
    local head_repo="${VDE_PR_HEAD_REPO-}"
    local base_repo="${VDE_PR_BASE_REPO-}"

    if [[ "${author}" == 'dependabot[bot]' ]]; then
        print -r -- "exempt: author is dependabot[bot], an automated dependency update"
        return 0
    fi
    # a fork may name its branch develop or stable: only the same repository counts as a promotion
    if [[ "${head}" == develop || "${head}" == stable ]] && [[ -n "${head_repo}" && "${head_repo}" == "${base_repo}" ]]; then
        print -r -- "exempt: head ref is ${head}, a promotion pull request from a permanent branch"
        return 0
    fi

    # Carriage returns (CRLF bodies) carry no meaning for the rules.
    body="${body//$'\r'/}"

    # Rule (a): the whole words RED and GREEN, case-insensitive.
    local folded="${(L)body}"
    folded="${folded//[^[:alnum:]_]/ }"
    local -a words
    words=( "${(@s: :)folded}" )
    if (( ${words[(Ie)red]} == 0 || ${words[(Ie)green]} == 0 )); then
        local missing=''
        (( ${words[(Ie)red]} )) || missing='RED'
        (( ${words[(Ie)green]} )) || missing="${missing:+${missing} and }GREEN"
        print -r -- "rule (a) failed: the body must contain the whole words RED and GREEN (missing: ${missing})" >&2
        return 1
    fi

    # Rule (c): the unmodified template placeholder must appear nowhere.
    if [[ "${body}" == *"${PLACEHOLDER}"* ]]; then
        print -r -- "rule (c) failed: the template placeholder (Paste terminal output here) is still in the body; replace it with the literal terminal output" >&2
        return 1
    fi

    # Rules (b) and (d): at least one CLOSED fenced block holds at least one
    # non-blank content line (the placeholder was already rejected by rule (c)). A fence opens with
    # three or more backticks or tildes (after optional spaces) and is closed
    # by the same fence character.
    local -a lines
    lines=( "${(@f)body}" )
    local line stripped rest trimmed fchar='' fence3=''
    local -i in_fence=0 has_content=0 block_ok=0
    for line in "${lines[@]}"; do
        stripped="${line##[[:space:]]#}"
        if (( in_fence )); then
            if [[ "${stripped}" == "${fence3}"* ]]; then
                rest="${stripped//${fchar}/}"
                rest="${rest//[[:space:]]/}"
                if [[ -z "${rest}" ]]; then
                    in_fence=0
                    if (( has_content )); then
                        block_ok=1
                        break
                    fi
                    continue
                fi
            fi
            trimmed="${stripped%%[[:space:]]#}"
            if [[ -n "${trimmed}" ]]; then
                has_content=1
            fi
        else
            if [[ "${stripped}" == '```'* ]]; then
                fchar='`'
            elif [[ "${stripped}" == '~~~'* ]]; then
                fchar='~'
            else
                continue
            fi
            fence3="${fchar}${fchar}${fchar}"
            in_fence=1
            has_content=0
        fi
    done

    if (( block_ok == 0 )); then
        print -r -- 'rule (b) failed: no closed fenced code block (``` or ~~~) holds a non-blank line of literal terminal output; rule (d): a block holding only the placeholder or blank lines does not count' >&2
        return 1
    fi

    print -r -- "pass: RED and GREEN are present, and a closed fenced block holds literal output"
    return 0
}

main "$@"
